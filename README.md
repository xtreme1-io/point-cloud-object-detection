# Docker image
`basicai/xtreme1-point-cloud-object-detection`

# Service
### Start
```shell
cd pcdet_open
python app.py <model file> --port xxxx
```
- `<model file>`：模型文件路径
- `--port`：port, defaut to 5000

### API
- URL：`POST http://ip:port/pointCloud/recognition:5000`
- Input

```json
{
    "datas": [
        {
            "id": 1,
            "pointCloudUrl": "https://path/to/xxx.pcd",
            "imageUrls": [
                "https://path/to/xxx.jpg",
                ...
            ],
            "cameraConfigUrl": "https://path/to/xxx.json"
        },
        ...
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
                ...
            ]
        },
        ...
    ]
}
```