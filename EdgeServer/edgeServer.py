import time
import socket
import threading
import sys
import base64
import random
import socket
import base64
import json

f = open("/tmp/logs/edgelog.txt", "w")
sys.stdout = f

data_processing_frac = {
    'mqtt': 80,
    'amqp': 85,
    'coap': 70,
    'zigbee': 75
}

processing_delays_size_frac = {
    'mqtt': 20,
    'amqp': 10,
    'coap': 30,
    'zigbee': 25
}

PERCENT_DELTA_DELAY = 6.9
PERCENT_DELTA_DATA = 8.9

server_address = ('127.0.0.1', 9000)

def handle_mqtt(data,protocol):
    size = sys.getsizeof(json.loads(base64.b64decode(data).decode())['payload'])
    percent_data_to_process = random.randrange(
        start=int(data_processing_frac[protocol] - PERCENT_DELTA_DATA),
        stop=int(data_processing_frac[protocol] + PERCENT_DELTA_DATA)
    )
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)
    
    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(data)
        retData = client_socket.recv(1024)
        client_socket.close()

    print("delay : ", delay)
    time.sleep(delay/1000)
    return data

def handle_ampq(data,protocol):
    size = sys.getsizeof(json.loads(base64.b64decode(data).decode())['payload'])
    percent_data_to_process = random.randrange(
        start=int(data_processing_frac[protocol] - PERCENT_DELTA_DATA),
        stop=int(data_processing_frac[protocol] + PERCENT_DELTA_DATA)
    )
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)
    
    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(data)
        retData = client_socket.recv(1024)
        client_socket.close()

    print("delay : ", delay)
    time.sleep(delay/1000)
    return data

def handle_coap(data,protocol):
    size = sys.getsizeof(json.loads(base64.b64decode(data).decode())['payload'])
    percent_data_to_process = random.randrange(
        start=int(data_processing_frac[protocol] - PERCENT_DELTA_DATA),
        stop=int(data_processing_frac[protocol] + PERCENT_DELTA_DATA)
    )
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)
    
    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(data)
        retData = client_socket.recv(1024)
        client_socket.close()

    print("delay : ", delay)
    time.sleep(delay/1000)
    return data

def handle_zigbee(data,protocol):
    size = sys.getsizeof(json.loads(base64.b64decode(data).decode())['payload'])
    percent_data_to_process = random.randrange(
        start=int(data_processing_frac[protocol] - PERCENT_DELTA_DATA),
        stop=int(data_processing_frac[protocol] + PERCENT_DELTA_DATA)
    )
    percent_delay = random.randrange(
        start=int(processing_delays_size_frac[protocol] - PERCENT_DELTA_DELAY),
        stop=int(processing_delays_size_frac[protocol] + PERCENT_DELTA_DELAY)
    )
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)
    
    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(data)
        retData = client_socket.recv(1024)
        client_socket.close()

    print("delay : ", delay)
    time.sleep(delay/1000)
    return data

def handle_client(clientsocket, address):
    while True:
        try:
            data = clientsocket.recv(1024)
            if data == b'':
                continue
            msg = json.loads(base64.b64decode(data).decode().strip())
            print(".................................................................data = ", data)
            print(msg)
    
            if msg['protocol'] == 'mqtt':
                handle_mqtt(data,msg['protocol'])
            elif msg['protocol'] == 'amqp':
                handle_ampq(data,msg['protocol'])
            elif msg['protocol'] == 'coap':
                handle_coap(data,msg['protocol'])
            elif msg['protocol'] == 'zigbee':
                handle_zigbee(data,msg['protocol'])

            clientsocket.send(data)
        except:
            clientsocket.send(b'')
            continue

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 8000))
    s.listen(10)
    thread_list = []

    while True:
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established!")
        t = threading.Thread(target=handle_client, args=(clientsocket, address))
        t.start()
        thread_list.append(t)
        print(f"Active Connections: {threading.activeCount() - 1}")

        for thread in thread_list:
            if not thread.is_alive():
                thread_list.remove(thread)