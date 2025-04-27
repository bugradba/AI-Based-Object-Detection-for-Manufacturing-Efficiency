from google.colab import drive
drive.mount('/content/drive')


!pip install ultralytics
from ultralytics import YOLO
import cv2

# 1. ADIM: MODEL EĞİTİMİ (Önce modeli eğitin)
def train_model():
    model = YOLO('yolov8n.pt')
    model.train(
        data='/content/drive/MyDrive/Dataset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        project='custom_model',
        name='patates_tespiti'
    )
train_model()

!pip install ultralytics
from ultralytics import YOLO
import cv2
from collections import Counter
from google.colab.patches import cv2_imshow

# ---> Sınıf isimleri
class_names = ['Bud-Sprouted', 'Defected potato', 'Diseases-fungal-damaged', 'Good']

def detect_video():
    model = YOLO('/content/best.pt')

    video_path = "test_videosu.mp4"
    cap = cv2.VideoCapture(video_path)

    output_path = "tespit_edilmis_video.mp4"
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # Toplam tespitler için sayaç
    total_counter = Counter()

    # ---> TXT dosyasını aç
    txt_file = open("tespit_sonuclari.txt", "w")

    frame_number = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_number += 1
        results = model(frame, conf=0.5)
        annotated_frame = results[0].plot()

        frame_counter = Counter()  # Bu frame'e özel sayaç

        if results[0].boxes.cls is not None:
            class_ids = results[0].boxes.cls.int().tolist()
            for cls_id in class_ids:
                if 0 <= cls_id < len(class_names):
                    frame_counter[class_names[cls_id]] += 1
                    total_counter[class_names[cls_id]] += 1

        # ---> Bu frame'deki sonuçları txt dosyasına yaz
        txt_file.write(f"Frame {frame_number}:\n")
        for class_name in class_names:
            txt_file.write(f"  {class_name}: {frame_counter.get(class_name, 0)}\n")
        txt_file.write("\n")  # Bir boş satır ekle

        out.write(annotated_frame)
        cv2_imshow(annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # ---> Döngü bitince txt dosyasına toplam sayıları yaz
    txt_file.write("\nToplam Tespitler:\n")
    for class_name in class_names:
        txt_file.write(f"{class_name}: {total_counter.get(class_name, 0)}\n")

    txt_file.close()  # txt dosyasını kapat

    print("\nTespit Edilen Nesne Sayıları (Toplam):")
    for class_name, count in total_counter.items():
        print(f"{class_name}: {count}")

if __name__ == "__main__":
    detect_video()
