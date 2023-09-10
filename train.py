import torch
from ultralytics import YOLO

print('available')
print(torch.cuda.is_available())

if __name__ == '__main__':
    model = YOLO('yolov8n.yaml')  # build a new model from YAML
    model.to('cuda')

    model.train(data='minimap.yaml', epochs=128, imgsz=640, device=[0, 1], cfg="balanced-approach.yaml")
    # model.train(data='minimap.yaml', epochs=128, imgsz=640, device=[0, 1], cfg="conservative-learning.yaml")