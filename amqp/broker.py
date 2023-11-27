import threading
from typing import Dict
import socket
import base64
import json

class Exchange:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._bindings: Dict[str, socket.socket] = {}

    def bind(self, routing_key, client: socket.socket) -> None:
        with self._lock:
            # check if key already exists
            if routing_key in self._bindings:
                raise Exception("Key{} already exists".format(routing_key))
            self._bindings[routing_key] = client

    def unbind(self, routing_key) -> None:
        with self._lock:
            self._bindings.pop(routing_key, None)
    
    def route_message(self, message: str, key: str) -> None:
        with self._lock:
            client = self._bindings.get(key)
            if client:
                client.sendall(message.encode())
            else:
                raise Exception("No client found for key: {}".format(key))

# TCP Server, aka our broker to listen to incoming connections
class Broker:
    def __init__(self, port: int, exchange: Exchange) -> None:
        self._port = port
        self._exchange = exchange
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('127.0.0.1', self._port))
    
    def start(self):
        self._socket.listen()
        print("Broker listening on port {}".format(self._port))
        while True:
            client, _ = self._socket.accept()
            # Handle client in a new thread
            threading.Thread(target=self._handle_client, args=(client,)).start()
    
    def _handle_client(self, client: socket.socket):
        with client:
            # Receive key
            try:
                key = client.recv(1024).decode()
                print(key)
                print(type(key))
            except Exception as e:
                print("Error receiving key: {}".format(e))
                client.sendall("Error receiving key: {}\nClosing your connection".format(e).encode())
                return
            # Bind client to exchange
            try:
                self._exchange.bind(key, client)
            except Exception as e:
                print("Error binding client to exchange: {}".format(e))
                client.sendall("Error binding you to exchange: {}".format(e).encode())
                return
            # Send ack for binding
            client.sendall(("You are now connected to the exchange with key: {}".format(key)).encode())
            print("Handling client: {}".format(client))
            while True:
                message = client.recv(1024)
                if message == b"close":
                    print("Closing connection to client: {}".format(client))
                    break
                # Parse message as json
                try:
                    message = base64.b64decode(message)
                except:
                    client.sendall(b"Message is not properly base64 encoded")
                    continue
                try:
                    msg_json = json.loads(message)
                except:
                    client.sendall(b"Message is not valid json")
                    continue
                # Check if message has routing key
                if 'key' not in msg_json:
                    client.sendall(b"Message has no routing key")
                    continue
                key = msg_json['key']
                print(key)
                # key = key.decode()
                # Check if message has payload
                if 'payload' not in msg_json:
                    client.sendall(b"Message has no payload")
                    continue
                msg_body = msg_json['payload']
                try:    
                    self._exchange.route_message(msg_body, key)
                except Exception as e:
                    print("Error routing message: {}".format(e))
                    client.sendall(("Error routing message: {}".format(e)).encode())
                    continue
            # Unbind client from exchange
            self._exchange.unbind(key)

if __name__ == "__main__":
    exchange = Exchange()
    print("Starting broker...")
    broker = Broker(5000, exchange)
    broker.start()
    print("Broker started")