from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)


results = model.train(data=r'C:\Users\yassine\Desktop\kilabor.v2i.yolov8\data.yaml', epochs=100, imgsz=640)
