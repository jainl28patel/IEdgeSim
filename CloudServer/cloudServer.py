import time
import socket
import threading
import sys
import base64
import random
import socket
import base64
import json

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

server_address = ('localhost', 12345)

def handle_mqtt(data,protocol):
    size = sys.getsizeof(data)
    percent_data_to_process = random.randrange(start=(data_processing_frac[protocol]-PERCENT_DELTA_DATA),
                                               stop=(data_processing_frac[protocol]+PERCENT_DELTA_DATA))
    percent_delay = random.randrange(start=(processing_delays_size_frac[protocol]-PERCENT_DELTA_DELAY),
                                     stop=(processing_delays_size_frac[protocol]+PERCENT_DELTA_DELAY))
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)

    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(base64.encode(json.dumps({'payload':data,'protocol':protocol})))
        retData = client_socket.recv()
        client_socket.close()

    time.sleep(delay)
    return retData

def handle_ampq(data,protocol):
    size = sys.getsizeof(data)
    percent_data_to_process = random.randrange(start=(data_processing_frac[protocol]-PERCENT_DELTA_DATA),
                                               stop=(data_processing_frac[protocol]+PERCENT_DELTA_DATA))
    percent_delay = random.randrange(start=(processing_delays_size_frac[protocol]-PERCENT_DELTA_DELAY),
                                     stop=(processing_delays_size_frac[protocol]+PERCENT_DELTA_DELAY))
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)

    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(base64.encode(json.dumps({'payload':data,'protocol':protocol})))
        retData = client_socket.recv()
        client_socket.close()

    time.sleep(delay)
    return retData

def handle_coap(data,protocol):
    size = sys.getsizeof(data)
    percent_data_to_process = random.randrange(start=(data_processing_frac[protocol]-PERCENT_DELTA_DATA),
                                               stop=(data_processing_frac[protocol]+PERCENT_DELTA_DATA))
    percent_delay = random.randrange(start=(processing_delays_size_frac[protocol]-PERCENT_DELTA_DELAY),
                                     stop=(processing_delays_size_frac[protocol]+PERCENT_DELTA_DELAY))
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)

    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(base64.encode(json.dumps({'payload':data,'protocol':protocol})))
        retData = client_socket.recv()
        client_socket.close()

    time.sleep(delay)
    return retData

def handle_zigbee(data,protocol):
    size = sys.getsizeof(data)
    percent_data_to_process = random.randrange(start=(data_processing_frac[protocol]-PERCENT_DELTA_DATA),
                                               stop=(data_processing_frac[protocol]+PERCENT_DELTA_DATA))
    percent_delay = random.randrange(start=(processing_delays_size_frac[protocol]-PERCENT_DELTA_DELAY),
                                     stop=(processing_delays_size_frac[protocol]+PERCENT_DELTA_DELAY))
    
    delay = (size * percent_delay) / 100
    percent_data_to_send = 100-percent_data_to_process
    randnum = random.randrange(start=0,stop=100)

    if randnum<percent_data_to_send:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(base64.encode(json.dumps({'payload':data,'protocol':protocol})))
        retData = client_socket.recv()
        client_socket.close()

    time.sleep(delay)
    return retData

def handle_client(clientsocket, address):
    while True:
        data = clientsocket.recv(1024)
        msg = json.loads(base64.decode(data))
        retData = None

        if msg['protocol'] == 'mqtt':
            retData = handle_mqtt(msg['payload'],msg['protocol'])
        elif msg['protocol'] == 'ampq':
            retData = handle_ampq(msg['payload'],msg['protocol'])
        elif msg['protocol'] == 'coap':
            retData = handle_coap(msg['payload'],msg['protocol'])
        elif msg['protocol'] == 'zigbee':
            retData = handle_zigbee(msg['payload'],msg['protocol'])

        clientsocket.send(retData)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 8000))
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

if __name__ == "__main__":
    main()