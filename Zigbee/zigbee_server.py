# server.py

import threading
import socket
import uuid
import base64
import json
import time
import sys

f = open("./log.txt", "w")
sys.stdout = f

class Node:
    def __init__(self, name):
        self.name = name
        self.network = None
        self.routing_table = {}
        self.address = str(uuid.uuid4())

    def join_network(self, network):
        self.network = network
        network.add_node(self)

    def leave_network(self):
        self.network.remove_node(self)
        self.network = None

    def send_message(self, recipient_address, message):
        print(f"Node {self.name} is sending message to Node with address {recipient_address}")
        print(f"Network nodes: {self.network.nodes}")
        if recipient_address in self.routing_table:
            next_node = self.routing_table[recipient_address]
            if next_node is not None:
                next_node.route_message(self.name, recipient_address, message)
        else:
            self.network.coordinator.route_message(self.name, recipient_address, message)

    def route_message(self, original_sender, recipient_address, message):
        if self.address == recipient_address:
            print(f"Node {self.name} received a message: {message}")
        else:
            self.routing_table[original_sender] = self
            self.send_message(recipient_address, message)


class Coordinator(Node):
    def __init__(self, name, network):
        super().__init__(name)
        self.network = network

    def start_network(self):
        print(f"Coordinator {self.name} is starting the network")

    def add_node_to_network(self, node):
        node.join_network(self.network)

    def route_message(self, sender_name, recipient_address, message):
        sender = next((node for node in self.network.nodes if node.name == sender_name), None)
        recipient = next((node for node in self.network.nodes if node.address == recipient_address), None)
        print(f"Sender: {sender}, Recipient: {recipient}")
        if sender and recipient:
            sender.routing_table[recipient_address] = recipient
            recipient.route_message(sender_name, recipient_address, message)


class Router(Node):
    def route_message(self, original_sender, recipient_address, message):
        super().route_message(original_sender, recipient_address, message)


class EndDevice(Node):
    def route_message(self, original_sender, recipient_address, message):
        print(f"EndDevice {self.name} received a message: {message}")


class Network:
    def __init__(self, coordinator):
        self.nodes = [coordinator]
        self.coordinator = coordinator

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def broadcast_message(self, sender, message):
        for node in self.nodes:
            if node != sender:
                node.route_message(sender.name, node.name, message)

class Cloud:
    def __init__(self, host: str, port: int):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def send_to_cloud(self, payload: str):
        msg = {
            'protocol' : 'zigbee' ,
            'payload': payload,
        }
        msg = json.dumps(msg)
        self._socket.sendall(base64.urlsafe_b64encode(msg.encode()))
    
    def recv_from_cloud(self) -> str:
        return self._socket.recv(1024)


class Server:
    def __init__(self, host, port):
        self.address = str(uuid.uuid4())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.socket.bind((self.host, self.port))
        self.network = Network(self)
        self.cloud = Cloud("127.0.0.1",8000)

    def start(self):
        self.socket.listen()
        print("Server listening on port {}".format(self.port))
        while True:
            client, _ = self.socket.accept()
            print("Client connected")
            threading.Thread(target=self._handle_client, args=(client,)).start()


    def _handle_client(self, client: socket.socket):
        with client:
            message = client.recv(1024).decode()
            msg = message.split(":")
            if(len(msg) > 2):
                data = {
                    "node" : msg[1],
                    "payload" : msg[2]
                }
                print(f"Received message: {data['payload']} at node {data['node']}")
                t1 = time.time()
                self.cloud.send_to_cloud(base64.b64encode(json.dumps(data).encode()).decode())
                print(f"Cloud response: {self.cloud.recv_from_cloud()}")
                t2 = time.time()
                print(f"Delay: {(t2-t1)*1000}ms")
            if message.startswith("register:"):
                client_address = message.split(":", 1)[1]
                print(f"Client addr {client_address}")
                node = next((n for n in self.network.nodes if n.address == client_address), None)
                if not node:
                    node = Node(client_address)
                    self.network.add_node(node)
            else:
                sender_address, message = message.split(":", 1)
                node = next((n for n in self.network.nodes if n.address == sender_address), None)
                if node:
                    node.route_message(node.address, sender_address, message)
                else:
                    print(f"No node found for address: {sender_address}")


if __name__ == "__main__":
    server = Server('127.0.0.1', 5003)
    server.start()

