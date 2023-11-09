import socket
import threading
import os
from time import sleep


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 8000))
    s.listen(5)

    while True:
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established!")
        t = threading.Thread(target=handle_client, args=(clientsocket, address))
        t.start()
        print(f"Active Connections: {threading.activeCount() - 1}")

def handle_client(clientsocket, address):
    while True:
        msg = clientsocket.recv(1024)
        sleep(1)
        print(f"Message from {address}: {msg.decode('utf-8')}")
        clientsocket.send(bytes(f"Message from {address}: {msg.decode('utf-8')}", "utf-8"))

if __name__ == "__main__":
    main()