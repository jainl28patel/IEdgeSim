import socket
import time
import random
import threading

SERVER_IP = '127.0.0.50'
SERVER_PORT = 5002
KEY = "Networks_Project"

class LoRaWAN_Packet:
    def __init__ (self, data):
        self.data = data
        
    def decrypt(self):
        temp = self.data
        encrypted = []
        for i in range(len(temp)):
            encrypted.append(chr(ord(temp[i]) ^ ord(KEY[i % len(KEY)])))
        check = ''.join(encrypted)
        return check
    def encrypt(self):
        return self.decrypt().encode()
        
class Client:
    def __init__(self):
        self._port = SERVER_PORT
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send(self, data):
        self._socket.sendto(data, (SERVER_IP, SERVER_PORT))

class Sensor:
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.value = 0
    def send_data(self, data):
        datasent = Client()
        datasent.send(data)

def node_(sensor_id: int):
    sensor = Sensor(sensor_id)
    while True:
        sensor.value = round(random.uniform(0, 100), 2)
        print(f"Sensor {sensor.sensor_id} is sending data")
        data = f"Sensor {sensor.sensor_id} - Data: {sensor.value}"
        findata = LoRaWAN_Packet(data)
        sensor.send_data(findata.encrypt())
        print("Data Sent")
        time.sleep(5)

if __name__ == "__main__":
    threads = list()
    for i in range (1,5):
        curthread = threading.Thread(target=node_, args=(i,))
        threads.append(curthread)
        curthread.start()
