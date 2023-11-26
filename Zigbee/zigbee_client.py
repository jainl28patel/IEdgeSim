# client.py
import threading
import socket
import uuid
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

class Client:
    def __init__(self, host, port):
        self.address = str(uuid.uuid4())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.network = Network(self)

    def register(self):
        self.socket.sendall(f"register:{self.address}".encode())

    def connect(self):
        self.socket.connect((self.host, self.port))
        print("Client connected to server")


    def send_message(self, message):
        print(f"Sending message: {message}")
        self.socket.sendall(f"{self.address}:{message}".encode())

def thread_function(num):
    client = Client('127.0.0.1', 5000)
    client.connect()
    client.register()
    client.send_message(f'Hello from client {num}')


if __name__ == "__main__":
    threads = list()
    for i in range(5):
        cli = threading.Thread(args=(i,),target=thread_function)
        threads.append(cli)
        cli.start()