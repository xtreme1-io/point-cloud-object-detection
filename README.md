# Point Cloud Object Detection

## Run

Create base image, which is based on [OpenPCDet](https://github.com/open-mmlab/OpenPCDet):
```bash
cd base_image
docker build -t basicai/xtreme1-point-cloud-object-detection-base .
```

Using the base image to run model service:
```bash
docker run -it --rm -p 5000:5000 -v ./:/app --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=0 -m 32G --memory-reservation 8G --cpu-shares=80 --shm-size=32G basicai/xtreme1-point-cloud-object-detection-base env LANG=C.UTF-8 /bin/bash

# The following commands run in the container
cd /app
wget https://basicai-asset.s3.us-west-2.amazonaws.com/xtreme1/model/cbgs_voxel0075_centerpoint_nds_6648.pth

cd pcdet_open
python app.py ../cbgs_voxel0075_centerpoint_nds_6648.pth --port 5000
```

## API

- URL：`POST http://ip:port/pointCloud/recognition`
- Input
```json
{
    "datas": [
        {
            "id": 1,
            "pointCloudUrl": "https://path/to/xxx.pcd",
            "imageUrls": [
                "https://path/to/xxx.jpg",
                // ...
            ],
            "cameraConfigUrl": "https://path/to/xxx.json"
        },
        // ...
    ]
}
```
- Output
```json
{
    "code": "OK",
    "message": "",
    "data": [
        {
            "id": 1,
            "code": "OK",
            "message": "",
            "objects": [
                {
                    "x": 200.1,
                    "y": 12.3,
                    "z": 28.7,
                    "dimX": 12,
                    "dimY": 22,
                    "dimZ": 32,
                    "rotX": 20,
                    "rotZ": 30,
                    "rotY": 10,
                    "confidence": 0.8,
                    "label": "car"
                },
                // ...
            ]
        },
        // ...
    ]
}
```