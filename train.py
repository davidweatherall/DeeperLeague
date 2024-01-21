import torch
from ultralytics import YOLO

print('available')
print(torch.cuda.is_available())
print(torch.backends.mps.is_available())

if __name__ == '__main__':
    model = YOLO('yolov8n.yaml')  # build a new model from YAML
    model.to('mps')

    model.train(data='minimap.yaml', epochs=128, imgsz=320, device='mps', cfg="balanced-approach.yaml")
    # model.train(data='minimap.yaml', epochs=128, imgsz=640, device=[0, 1], cfg="conservative-learning.yaml")