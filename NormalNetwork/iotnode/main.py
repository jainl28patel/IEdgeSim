import socket
import threading
import random
from time import sleep

def main():
    # write client code here

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 8000))

    while True:
        # send random number to server
        msg = random.randint(0, 100)
        sleep(1)
        s.send(bytes(str(msg), "utf-8"))
        print(s.recv(1024).decode("utf-8"))

    s.close()

if __name__ == "__main__":
    main()