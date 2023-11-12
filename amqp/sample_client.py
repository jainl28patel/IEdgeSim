# TCP client to connect to server running on port 5000 on localhost

"""
This contains of an example code to connect to the message broker and send and receive messages

Each connector represents either a cloud server, an edge device or a local IoT device
"""

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

import time

if __name__ == "__main__":
    client = Client(5000)
    # Send key
    client.send(b"key1")
    # Receive ack
    print(client.recv())
    # Send message
    msg = {
        'key': 'key1',
        'payload': 'Hello world!'
    }
    msg = json.dumps(msg)
    client.send(base64.urlsafe_b64encode(msg.encode()))
    # Receive ack
    print(client.recv())
    time.sleep(1)
    # Send close
    client.send(b"close")
    # Close connection
    client.close()