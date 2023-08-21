import numpy as np
from pcdet_open.service import *

from pcdet_open.src.load_pcd import PointCloud
from pcdet_open.src.predictor import Predictor

import io
import requests
from os.path import join, dirname, abspath
import gc


class AppHandler(BaseApiHandler):
    predictor = None

    # override: Called for each request.
    def initialize(self, cfg_file: str, ckpt: str):
        if AppHandler.predictor is None:
            AppHandler.predictor = Predictor(cfg_file=cfg_file, ckpt=ckpt)

    # override
    def post(self):
        args = self.args
        datas = self.get_field(args, key='datas', type_=list, check_empty=True)

        results = [self.process_data(data) for data in datas]

        # clean up memory to avoid OOM
        gc.collect()

        self.return_ok(results)

    @staticmethod
    def _build_item_error(code: str, message: str, id: int = None):
        return {
            "id": id,
            "code": code,
            "message": message
        }

    def process_data(self, data):
        if not isinstance(data, dict):
            return self._build_item_error("InvalidArgument", "data must be a dictionary")

        id = data.get("id", None)
        if id is None:
            return self._build_item_error("InvalidArgument", 'missing "id"')

        pcd_url = self.get_field(data, key='pointCloudUrl', type_=str)
        if pcd_url is None:
            return self._build_item_error("InvalidArgument", 'missing "pointCloudUrl"')

        try:
            t = Timing()
            logging.info(f"{'-'*10} {pcd_url} {'-'*10}")

            # download
            r = requests.get(pcd_url, allow_redirects=True)
            t.log_interval(f"DOWNLOAD pcd({len(r.content)/1024/1024:.2g}MB)")

            # load pcd
            pcd_path = io.BytesIO(r.content)
            pc = PointCloud(pcd_path).normalized_numpy()
            t.log_interval(f"LOAD pcd")

            # remove nan and zeros
            count1 = len(pc)
            pc = pc[~np.isnan(pc[:, :3]).any(axis=1)]
            count2 = len(pc)
            if count2 < count1:
                logging.info(f"\tremove {count1 - count2} nan points")
            
            pc = pc[(pc[:, :3] != 0).any(axis=1)]
            count3 = len(pc)
            if count3 < count2:
                logging.info(f"\tremove {count2 - count3} zero points")
            t.log_interval(f"VALIDATE points")

            # predict
            results, _ = self.predictor(points=pc, full_nms=True)
            t.log_interval(f"MODEL run")
            logging.info(f"{pc.shape} => {len(results['pred_boxes'])} objects")
        except Exception as e:
            logging.exception(e)
            return self._build_item_error("SystemError", str(e), id=id)

        class_names = self.predictor.class_names
        objects = [
            {
                "label": class_names[label-1].upper(),
                "confidence": score,

                "x": box[0],
                "y": box[1],
                "z": box[2],
                "dx": box[3],
                "dy": box[4],
                "dz": box[5],
                "rotX": 0,
                "rotY": 0,
                "rotZ": box[6]
            }
            for box, score, label in zip(
                results['pred_boxes'].astype(np.float64).round(3).tolist(),
                results['pred_scores'].astype(np.float64).round(3).tolist(),
                results['pred_labels'].tolist())
        ]

        return {
            "id": id,
            "code": "OK",
            "message": "",
            "objects": objects
        }


def main():
    parser = ArgumentParser()
    parser.add_argument('ckpt', type=str, help='model file')
    args = parse_args(parser)

    app_dir = dirname(abspath(__file__))
    cfg_file = join(app_dir, 'cfgs', 'nuscenes_models', 'cbgs_voxel0075_res3d_centerpoint.yaml')
    ckpt = args.ckpt

    start_service([
            (r'/pointCloud/recognition', AppHandler, dict(cfg_file=cfg_file, ckpt=ckpt)),
        ],
        args)


if __name__ == '__main__':
    main()
