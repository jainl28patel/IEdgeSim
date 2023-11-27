import socket
import threading
import time

class Client:
    def __init__(self, port):
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
    client = Client(5001)

    client.send(b"AuthRequest")

    print("{}: {}".format(num, client.recv()))

    while True:
        client.send(b"rts")
        res = client.recv()
        if res == b"cts":
            client.send(f"Hello from {num}".encode())

        time.sleep(5)


if __name__ == "__main__":
    time.sleep(2)
    threads = list()
    for i in range(1,6):
        z = threading.Thread(target=thread_function,args=(i,))
        threads.append(z)
        z.start()
        time.sleep(1)