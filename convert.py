from ultralytics import YOLO


if __name__ == '__main__':
    model = YOLO("./runs/detect/train/weights/best.pt")

    # Export the model
    model.export(format="tfjs")