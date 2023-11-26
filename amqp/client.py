# TCP client to connect to server running on port 5000 on localhost
# Creates 5 client nodes (using threads) to send payloads to node with key='key0'
 
import socket
import json
import base64
import threading
import time

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


def thread_function(num: int):
    time.sleep(num)
    client = Client(5000)
    key = f"key{num}"
    payload = f"Hello from {num}"
    # Send key
    client.send(key.encode())
    # Receive ack
    print(client.recv())
    while True:
        # Send message
        msg = {
            'key': 'key0',
            'payload': payload
        }
        msg = json.dumps(msg)
        client.send(base64.urlsafe_b64encode(msg.encode()))
        
        
        time.sleep(5)


if __name__ == "__main__":
    threads = list()
    for i in range(1,6):
        z = threading.Thread(target=thread_function,args=(i,))
        threads.append(z)
        z.start()