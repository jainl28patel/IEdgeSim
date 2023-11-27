import socket
import threading
import base64
import json
import sys
import time

SERVER_IP = '127.0.0.50'
SERVER_PORT = 5000
KEY = "Networks_Project"
CLOUD_HOST = "127.0.0.1"
CLOUD_PORT = 8000

f = open("./log.txt","w+")
sys.stdout = f

class Server:
    def __init__(self, host: str, port: int):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
    
    def send_to_cloud(self, payload: str):
        msg = {
            'protocol' : 'lorawan' ,
            'payload': payload
        }
        msg = json.dumps(msg)
        self._socket.sendall(base64.urlsafe_b64encode(msg.encode()))
             
    def recv_from_cloud(self) -> str:
        data = self._socket.recv(1024)
        return data

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
    
class GateWay:
    server = Server(CLOUD_HOST, CLOUD_PORT)
    def __init__(self):
        self.server = Server(CLOUD_HOST, CLOUD_PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((SERVER_IP, SERVER_PORT))
        self.is_running = False
        self.receive_thread = threading.Thread(target=self.receive_data)

    def start(self):
        self.is_running = True
        self.receive_thread.start()
        print("Gateway started. Waiting for data...")

    def stop(self):
        self.is_running = False
        self.server_socket.close()
        self.receive_thread.join()
        print("\Gateway stopped.")

    def receive_data(self):
        while self.is_running:
            data, address = self.server_socket.recvfrom(1024)
            packet = LoRaWAN_Packet(data.decode())
            decrypted_data = packet.decrypt()
            print("Received data:", decrypted_data)
            t1 = time.time()
            self.server.send_to_cloud(decrypted_data)
            print("Data sent to Cloud")
            response_cloud = self.server.recv_from_cloud()
            t2 = time.time()
            print(f"Response from the Cloud: {response_cloud.decode()}")
            print(f"Delay: {(t2-t1)*1000}ms")

if __name__ == "__main__":
    server = GateWay()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
