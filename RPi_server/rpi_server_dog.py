import socket
import threading
import time
from RPi import GPIO
from lcd import LCD
from rgb_led import RGB_LED
import os
import yaml

BASE_DIR     = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
config_path  = os.path.join(BASE_DIR, 'config.yaml')
classes_path = os.path.join(BASE_DIR, 'classes.txt')

with open(config_path, 'r') as f:
    cfg = yaml.safe_load(f)

with open(classes_path, 'r') as f:
    class_names = [line.strip() for line in f if line.strip()]

HOST = cfg['server']['host']
PORT = cfg['server']['port']
THRESHOLD = cfg['confidence_threshold']

BUTTON_PIN = 21
RGB_LED_RED_PIN = 5
RGB_LED_GREEN_PIN = 6
RGB_LED_BLUE_PIN = 13

rgb_led = RGB_LED(RGB_LED_RED_PIN, RGB_LED_GREEN_PIN, RGB_LED_BLUE_PIN)
lcd     = LCD(0x27)
lcd.init_LCD()
led_on  = True
server_socket = None
down_flag = threading.Event()

def button_callback(channel):
    global led_on
    led_on = not led_on
    if not led_on:
        rgb_led.turn_off()
    print(f"[Button] LED toggled {'ON' if led_on else 'OFF'}")

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        BUTTON_PIN,
        GPIO.FALLING,
        callback=button_callback,
        bouncetime=200
    )


def accept_connections():
    server_socket.settimeout(0.2)
    while not down_flag.is_set():
        try:
            client_sock, addr = server_socket.accept()
            print(f"[Socket] Connection from {addr}")
            threading.Thread(
                target=handle_client,
                args=(client_sock,),
                daemon=True
            ).start()
        except socket.timeout:
            continue


def handle_client(sock):
    sock.settimeout(0.2)
    try:
        while not down_flag.is_set():
            try:
                data = sock.recv(1024)
                if not data:
                    break
            except socket.timeout:
                continue
            msg = data.decode().strip()
            if not msg:
                continue
            parts = msg.split(', ')
            if len(parts) != 2:
                print(f"[Socket] Bad message: {msg}")
                continue
            idx_str, conf_str = parts
            idx  = int(float(idx_str))
            conf = float(conf_str)
            if conf < THRESHOLD or idx < 0 or idx >= len(class_names):
                continue
            emotion = class_names[idx]
            lcd.clear_display()
            lcd.send_string(emotion, 1)
            lcd.send_string(f"{conf*100:.1f}%", 2)

            if led_on:
                color_map = {
                    'happy':   'green',
                    'sad':     'blue',
                    'angry':   'red',
                    'relaxed': 'white'
                }
                rgb_led.set_color(color_map.get(emotion, 'white'))
    except Exception as e:
        print(f"[Socket] Error: {e}")
    finally:
        sock.close()

def cleanup():
    print("[Cleanup] Shutting down hardware...")
    try: lcd.clear_display()
    except: pass
    try: rgb_led.turn_off()
    except: pass
    try: rgb_led.cleanup()
    except: pass
    try: GPIO.cleanup()
    except: pass

if __name__ == "__main__":
    try:
        setup_GPIO()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        threading.Thread(target=accept_connections, daemon=True).start()
        print(f"[Socket] Server listening on {HOST}:{PORT}")
        while not down_flag.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("[Server] KeyboardInterrupt, shutting down")
        down_flag.set()
    finally:
        cleanup()
        if server_socket:
            server_socket.close()
        print("[Server] Stopped gracefully")

