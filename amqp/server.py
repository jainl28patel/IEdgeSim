# Server is node with key='key0' 
# It forwards any payload it recives to the Cloud Server

import socket
import json
import base64

class Client:
    def __init__(self, port: int):
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(('127.0.0.1', self._port))

    def send(self, data):
        self._socket.sendall(data)

    def recv(self):
        return self._socket.recv(1024)
    
    def close(self):
        self._socket.close()

class Server:
    def __init__(self, host: str, port: int):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
    
    def send_to_cloud(self, payload: str):
        msg = {
            'protocol' : 'amqp' ,
            'payload': payload
        }
        msg = json.dumps(msg)
        self._socket.sendall(base64.urlsafe_b64encode(msg.encode()))


import time

if __name__ == "__main__":
    # initializes cloud server
    cloud_host = "127.0.0.1"
    cloud_port = 8000
    server = Server(cloud_host,cloud_port)
    
    #amqp client
    client = Client(5000)
    
    client.send(b"key0")
    print(client.recv())
    
    # Send greeting to cloud
    msg = {
        'key': 'key0',
        'payload': 'Hello Cloud from key 0!'
    }
    msg = json.dumps(msg)
    client.send(base64.urlsafe_b64encode(msg.encode()))
    
    while True:
        # recieve payload from broker and send to cloud
        payload = client.recv().decode()
        print(payload)
        server.send_to_cloud(payload)
        time.sleep(1)