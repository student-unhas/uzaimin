import os
import Adafruit_DHT
import RPi.GPIO as GPIO
import cv2
from datetime import datetime
from threading import Thread
import csv

# Konfigurasi pin untuk sensor
dht_pin = 4  # suhu dan kelembaban
ldr_pin = 14  # cahaya
ph_pin = 23  # pH

# Inisialisasi sensor suhu
sensor = Adafruit_DHT.DHT11

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ldr_pin, GPIO.IN)
GPIO.setup(ph_pin, GPIO.IN)

# Buat direktori untuk menyimpan data jika belum ada
folder_name = "static/images"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Nama file CSV
csv_filename = "sensor_data.csv"

# Fungsi untuk menyimpan data ke CSV
def save_to_csv(data):
    file_exists = os.path.isfile(csv_filename)
    
    # Buka file CSV dalam mode append
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Jika file belum ada, tulis header terlebih dahulu
        if not file_exists:
            writer.writerow(["Timestamp", "Temperature", "Humidity", "Light Intensity", "pH", "Image Filename"])
        
        # Tulis data sensor ke file CSV
        writer.writerow([data["timestamp"], data["temperature"], data["humidity"], data["light_intensity"], data["ph"], data["image"]])

# Fungsi untuk membaca nilai sensor pH
def read_ph_sensor():
    ph_value = GPIO.input(ph_pin)
    if ph_value == GPIO.HIGH:
        return 7.0  # Misalnya, nilai pH netral
    else:
        return 4.0  # Misalnya, nilai pH asam

# Fungsi untuk resize gambar tanpa mengurangi kualitas
def resize_image(image, width=None, height=None, inter=cv2.INTER_AREA):
    # Dapatkan dimensi asli gambar
    (h, w) = image.shape[:2]
    
    # Jika baik width maupun height tidak ditentukan, kembalikan gambar asli
    if width is None and height is None:
        return image

    # Jika hanya width yang diberikan, hitung tinggi yang sesuai
    if width is not None:
        ratio = width / float(w)
        dimension = (width, int(h * ratio))

    # Jika hanya height yang diberikan, hitung lebar yang sesuai
    if height is not None:
        ratio = height / float(h)
        dimension = (int(w * ratio), height)

    # Ubah ukuran gambar dengan dimensi yang telah dihitung
    resized = cv2.resize(image, dimension, interpolation=inter)

    return resized

# Fungsi untuk menyimpan gambar yang diambil dari kamera
def save_image(frame):
    # Ubah ukuran gambar sebelum menyimpannya (contoh, lebar maksimum 300px)
    resized_frame = resize_image(frame, width=300)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f'{folder_name}/captured_image_{timestamp}.jpg'
    
    # Simpan gambar yang telah diubah ukurannya
    cv2.imwrite(image_filename, resized_frame)
    
    return image_filename

# Fungsi untuk menangkap data sensor
def capture_data():
    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    sensor_status = {
        'camera': True,
        'temperature_humidity': True,
        'light': True,
        'ph': True
    }

    # Cek apakah kamera berfungsi
    if not cap.isOpened():
        image_filename = None
        sensor_status['camera'] = False
    else:
        ret, frame = cap.read()
        if ret:
            thread = Thread(target=save_image, args=(frame,))
            thread.start()
            image_filename = f'{folder_name}/captured_image_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        else:
            image_filename = None
            sensor_status['camera'] = False

    cap.release()

    # Baca suhu dan kelembaban dari sensor
    humidity, temperature = Adafruit_DHT.read_retry(sensor, dht_pin)
    if humidity is None or temperature is None:
        sensor_status['temperature_humidity'] = False

    # Baca intensitas cahaya dari sensor LDR
    light_intensity = GPIO.input(ldr_pin)
    light_value = 1 if light_intensity == GPIO.HIGH else 0  # 1 untuk terang, 0 untuk gelap

    # Baca nilai pH
    ph = read_ph_sensor()

    # Buat dictionary untuk data sensor
    sensor_data = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "temperature": temperature if sensor_status['temperature_humidity'] else "Sensor Error",
        "humidity": humidity if sensor_status['temperature_humidity'] else "Sensor Error",
        "light_intensity": light_value if sensor_status['light'] else "Sensor Error",
        "ph": ph if sensor_status['ph'] else "Sensor Error",
        "image": image_filename if sensor_status['camera'] else None,
        "status": "Semua sensor berfungsi dengan baik." if all(sensor_status.values()) else "Beberapa sensor mengalami kesalahan."
    }

    # Simpan data ke file CSV
    save_to_csv(sensor_data)

    return sensor_data
