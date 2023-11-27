import time
import socket
import threading
import sys
import base64
import random
import socket
import base64
import json

f = open("/tmp/logs/cloudlog.txt", "w+")

data_processing_frac = {
    'mqtt': 80,
    'ampq': 85,
    'coap': 70,
    'zigbee': 75
}

processing_delays_size_frac = {
    'mqtt': 20,
    'ampq': 10,
    'coap': 30,
    'zigbee': 25
}

PERCENT_DELTA_DELAY = 6.9
PERCENT_DELTA_DATA = 8.9

def handle_mqtt(data,protocol):
    size = sys.getsizeof(data)
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )
    
    delay = (size * percent_delay) / 100
    f.write("delay : " + str(delay) + "\n")
    f.write("data : " + str(data) + "\n")
    f.write("size : " + str(size) + "\n")
    time.sleep(delay/1000)
    return data

def handle_ampq(data,protocol):
    size = sys.getsizeof(data)
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )

    delay = (size * percent_delay) / 100
    time.sleep(delay/1000)
    return data

def handle_coap(data,protocol):
    size = sys.getsizeof(data)
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )

    delay = (size * percent_delay) / 100
    time.sleep(delay/1000)
    return data

def handle_zigbee(data,protocol):
    size = sys.getsizeof(data)
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )
    
    delay = (size * percent_delay) / 100
    time.sleep(delay/1000)
    return data

def handle_client(clientsocket, address):
    data = clientsocket.recv(1024)
    msg = json.loads(base64.b64decode(data).decode().strip())

    if msg['protocol'] == 'mqtt':
        handle_mqtt(msg['payload'],msg['protocol'])
    elif msg['protocol'] == 'ampq':
        handle_ampq(msg['payload'],msg['protocol'])
    elif msg['protocol'] == 'coap':
        handle_coap(msg['payload'],msg['protocol'])
    elif msg['protocol'] == 'zigbee':
        handle_zigbee(msg['payload'],msg['protocol'])

    clientsocket.send(data)
    clientsocket.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 9000))
    s.listen(10)
    thread_list = []

    while True:
        clientsocket, address = s.accept()
        f.write(f"Connection from {address} has been established!")
        t = threading.Thread(target=handle_client, args=(clientsocket, address))
        t.start()
        thread_list.append(t)
        f.write(f"Active Connections: {threading.activeCount() - 1}")

        for thread in thread_list:
            if not thread.is_alive():
                thread_list.remove(thread)