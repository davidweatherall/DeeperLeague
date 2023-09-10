from ultralytics import YOLO
from PIL import Image


model = YOLO("models/balanced-approach/weights/best.pt")
buf = Image.open("example_cropped_image.png")
results = model.predict(buf)
result = results[0]
output = []
for box in result.boxes:
  x1, y1, x2, y2 = [
    round(x) for x in box.xyxy[0].tolist()
  ]
  class_id = box.cls[0].item()
  prob = round(box.conf[0].item(), 2)
  output.append([
    x1, y1, x2, y2, result.names[class_id], prob
  ])

[print(f"{name}: ({x1},{y1},{x2},{y2}) - {prob} chance") for x1, y1, x2, y2, name, prob in output]
