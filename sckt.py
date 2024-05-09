import cv2
import numpy as np
import socket
from picamera2 import Picamera2, Preview
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import pickle
from time import sleep
import math

# Raspberry Pi'nin IP adresi ve kullanacağınız port numarasını buraya yazın
RPI_IP = '0.0.0.0'  # Raspberry Pi'nin IP adresi
PC_IP = '192.168.1.107'
PORT = 12350     # Kullanılacak port numarası

MESSAGE_PORT = 12345

# Kamera aç
picam = Picamera2()

config = picam.create_preview_configuration()
picam.configure(config)

factory = PiGPIOFactory()

# servo1 motoru oluştur
servo1 = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory) # Y angle
servo2 = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory) # X angle



# Soket oluştur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((RPI_IP, PORT))
server_socket.listen(5)


print("Bağlantı bekleniyor")

client_socket, address = server_socket.accept()

print("Bağlantı alındı:", address)

sleep(10)

pc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pc_socket.connect((PC_IP, MESSAGE_PORT))

print("Bilgisayara bağlandı")


picam.start()
try:
    while True:
        # Kameradan görüntüyü al
        frame = picam.capture_array()
        
        # Görüntüyü baytlara dönüştür
        _, img_encoded = cv2.imencode('.bmp', frame)
        data = np.array(img_encoded)
        string_data = data.tobytes()
       

        # Görüntüyü gönder
        client_socket.sendall((str(len(string_data))).encode().ljust(16) + string_data)
        
        data = pc_socket.recv(4096)
        if(data):
            servo_angles = pickle.loads(data)
            print(servo_angles)
            servo1.value = math.sin(math.radians(servo_angles["y_client"]))
            servo2.value = math.sin(math.radians(servo_angles["x_client"]))
except KeyboardInterrupt:
    print("\nKullanıcı tarafından işlem iptal edildi.")
finally:
    # Kamera ve soketleri kapat
    camera.release()
  
  