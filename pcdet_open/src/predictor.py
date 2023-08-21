import glob
from pathlib import Path
import numpy as np
import logging
import torch

from pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.models.model_utils import model_nms_utils


class DemoDataset(DatasetTemplate):
    def __init__(self, points: np.ndarray, dataset_cfg, class_names):
        super().__init__(
            dataset_cfg=dataset_cfg, class_names=class_names, training=False, root_path=None, logger=logging
        )

        if points is not None:
            points = self._normalize_points(points)
            # add timestamp channel for nuscenes model
            if self.point_feature_encoder.num_point_features == 5:
                points = np.hstack([points, np.zeros((points.shape[0], 1))])

        self.points = points

    @staticmethod
    def _normalize_points(points):
        B, C = points.shape
        if C < 3:
            raise ValueError(f"Invalid points with shape {points.shape}")
        elif C == 3:
            points = np.hstack([points, np.zeros((B, 1))])
        else:
            points = points[:, :4]

        _min, _max = points[:, 3].min(), points[:, 3].max()
        if _min < 0.0 or _max > 1.0:
            points[:, 3] = (points[:, 3] - _min) / (_max - _min)
            logging.debug(f'normalize intensity from ({_min}, {_max}) to (0, 1)')
        return points

    def __len__(self):
        return 1

    def __getitem__(self, index):
        input_dict = {
            'points': self.points,
            'frame_id': index,
        }

        data_dict = self.prepare_data(data_dict=input_dict)
        return data_dict


class Predictor:
    def __init__(self, cfg_file, ckpt):
        cfg_from_yaml_file(cfg_file, cfg)

        self.class_names = cfg.CLASS_NAMES
        demo_dataset = DemoDataset(points=None, dataset_cfg=cfg.DATA_CONFIG, class_names=self.class_names)
        model = build_network(model_cfg=cfg.MODEL, num_class=len(self.class_names), dataset=demo_dataset)
        model.load_params_from_file(filename=ckpt, logger=logging)
        model.cuda()
        model.eval()
        self.model = model

    def __call__(self, points: np.ndarray = None, full_nms=True) -> tuple:
        assert points is not None, "points can not be None"

        dataset = DemoDataset(
            dataset_cfg=cfg.DATA_CONFIG, class_names=cfg.CLASS_NAMES, points=points
        )

        with torch.no_grad():
            data_dict = dataset[0]
            if len(data_dict['points']) > 100:
                data_dict = dataset.collate_batch([data_dict])
                load_data_to_gpu(data_dict)
                pred_dicts, _ = self.model.forward(data_dict)
                predicts = pred_dicts[0]
            
                if full_nms:
                    selected, selected_scores = model_nms_utils.class_agnostic_nms(
                        box_scores=predicts['pred_scores'],
                        box_preds=predicts['pred_boxes'],
                        nms_config=self.model.model_cfg.DENSE_HEAD.POST_PROCESSING['NMS_CONFIG']
                    )

                    predicts['pred_boxes'] = predicts['pred_boxes'][selected]
                    predicts['pred_scores'] = selected_scores
                    predicts['pred_labels'] = predicts['pred_labels'][selected]
            else:
                logging.info("empty point")
                predicts = {
                    'pred_boxes': np.empty((0, 9)),
                    'pred_scores':np.empty((0,)),
                    'pred_labels': np.empty((0,))
                }

            results = {
                k: v.cpu().numpy()
                for k, v in predicts.items()
            }

            return results, dataset.points
