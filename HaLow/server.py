import threading
import socket
from typing import Dict
import base64
import json
import time

class State:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: Dict[int, socket.socket] = {}
        self.send_queue = []
        self.sender_allowed = 0
        self.cid = 0

    def get_sender_allowed(self):
        with self._lock:
            return self.sender_allowed

    def get_cid(self):
        with self._lock:
            return self.cid

    def inc_cid(self):
        with self._lock:
            self.cid = self.cid + 1

    def add_send_queue(self, id):
        with self._lock:
            self.send_queue.append(id)

    def get_send_queue_len(self):
        with self._lock:
            return len(self.send_queue)

    def pop_send_queue(self):
        with self._lock:
            if(len(self.send_queue) > 0):
                x = self.send_queue.pop(0)
                self.sender_allowed = x
                self._clients.get(x).sendall(b"cts")
            else:
                self.sender_allowed = 0

    def bind(self, client_id, client: socket.socket) -> None:
        with self._lock:
            if client_id not in self._clients:
                self._clients[client_id] = client

    def unbind(self, client_id) -> None:
        with self._lock:
            self._clients.pop(client_id, None)

    def route_message(self, message: str, client_id: int) -> None:
        with self._lock:
            client = self._clients.get(client_id)
            if client:
                client.sendall(message)
            else:
                raise Exception("No client found for client_id: {}".format(client_id))

class Cloud:
    def __init__(self, host: str, port: int):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def send_to_cloud(self, payload: str):
        msg = {
            'protocol' : 'halow' ,
            'payload': payload,
        }
        msg = json.dumps(msg)
        self._socket.sendall(base64.urlsafe_b64encode(msg.encode()))
    
    def recv_from_cloud(self) -> str:
        return self._socket.recv(1024)

class Server:
    def __init__(self, port, state: State) -> None:
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('127.0.0.1', self._port))
        self.clients = state
        self.cloud = Cloud("127.0.0.1",8000)
        
    def start(self):
        self._socket.listen()
        print("Server listening on port {}".format(self._port))
        while True:
            client, _ = self._socket.accept()
            self.clients.inc_cid()
            threading.Thread(target=self._handle_client, args=(client,self.clients.get_cid())).start()

    def _handle_client(self, client: socket.socket, cid: int):
        with client:
            message = client.recv(1024)
            if message == b"AuthRequest":
                print("Authenticating client {}".format(cid))
                # -- authentication --
                self.clients.bind(cid, client)
                print("Client {} authenticated!".format(cid))
                client.sendall(b"Authenticated!")

            while True:
                message = client.recv(1024)
                if message == b"rts":
                    self.clients.add_send_queue(cid)
                    print(self.clients.get_send_queue_len())
                    if self.clients.get_send_queue_len() == 1:
                        self.clients.pop_send_queue()
                elif message == b"close":
                    print("Closing connection to client: {}".format(cid))
                    break
                elif self.clients.get_sender_allowed() == cid:
                    print("Message from client {}: {}".format(cid, message))
                    msg = {
                        "cid" : cid,
                        "data": message.decode() 
                    }
                    t1 = time.time()
                    self.cloud.send_to_cloud(json.dumps(msg))
                    print(f"Data from Edge: {self.cloud.recv_from_cloud()}")
                    t2 = time.time()
                    print(f"time = {(t2-t1)*1000}ms")
                    self.clients.pop_send_queue()

            self.clients.unbind(cid)

if __name__ == "__main__":
    print("Starting Server...")
    state = State()
    server = Server(5001, state)
    server.start()