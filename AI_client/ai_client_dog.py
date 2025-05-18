import cv2
from ultralytics import YOLO
import socket
import threading
import time
import sys
import os
import yaml

BASE_DIR     = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
config_path  = os.path.join(BASE_DIR, 'config.yaml')
classes_path = os.path.join(BASE_DIR, 'classes.txt')

with open(config_path, 'r') as f:
    cfg = yaml.safe_load(f)

with open(classes_path, 'r') as f:
    class_names = [line.strip() for line in f if line.strip()]

MODEL_PATH = cfg['model_path']
HOST = cfg['server']['host']
PORT = cfg['server']['port']
THRESHOLD = cfg['confidence_threshold']

client_socket = None
shutdown_flag = threading.Event() 

def setup_socket_client():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"[Client] Connected to {HOST}:{PORT}")
    threading.Thread(target=receive_messages,
                     args=(client_socket,),
                     daemon=True).start()

def receive_messages(sock):
    sock.settimeout(0.5)
    try:
        while not shutdown_flag.is_set():
            try:
                data = sock.recv(1024)
                if data:
                    print("[Server] " + data.decode().strip())
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[Client] Receive error: {e}")
    finally:
        sock.close()

def main():
    setup_socket_client()
    model = YOLO(MODEL_PATH)
    cap   = cv2.VideoCapture(0)
    prev_detections = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            current = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf   = float(box.conf[0])
                    if conf < THRESHOLD:
                        continue
                    emotion = class_names[cls_id]
                    current.append((cls_id, conf))
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(frame,
                                f"{emotion} {conf:.2f}",
                                (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0,255,0), 2)
            if current and current != prev_detections:
                for cls_id, conf in current:
                    msg = f"{cls_id}, {conf:.2f}"
                    try:
                        client_socket.sendall(msg.encode())
                    except Exception as e:
                        print(f"[Client] Send error: {e}")
                prev_detections = current

            cv2.imshow('PawTalk', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("[Client] KeyboardInterrupt, exiting")
    finally:
        shutdown_flag.set()
        cap.release()
        cv2.destroyAllWindows()
        if client_socket:
            client_socket.close()
        print("[Client] Stopped gracefully")

if __name__ == "__main__":
    main()
