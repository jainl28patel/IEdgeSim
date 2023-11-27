import socket
import struct
import threading
import json
import time
import base64
import sys

CLOUD_HOST = "127.0.0.1"
CLOUD_PORT = 8000

f = open("/tmp/logs/CoAPServerlog.txt", "w+")

class Server:
    def __init__(self, host: str, port: int):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
    
    def send_to_cloud(self, payload: str):
        msg = {
            'protocol' : 'coap' ,
            'payload': payload
        }
        msg = json.dumps(msg)
        self._socket.sendall(base64.urlsafe_b64encode(msg.encode()))
             
    def recv_from_cloud(self) -> str:
        data = self._socket.recv(1024)
        return data
        

class ThreadSafeResourceRepository:
    def __init__(self):
        self.lock = threading.Lock()
        self.resources = {}

    def get_resource(self, uri):
        with self.lock:
            return self.resources.get(uri)

    def update_resource(self, uri, data):
        with self.lock:
            self.resources[uri] = data

    def delete_resource(self, uri):
        with self.lock:
            if uri in self.resources:
                del self.resources[uri]

    def get_all_resources(self):
        with self.lock:
            return dict(self.resources)


class CoAPServer:
    server = Server(CLOUD_HOST, CLOUD_PORT)
    
    def __init__(self, bind_address, bind_port, resource_repository):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((bind_address, bind_port))
        self.resource_repository = resource_repository
        f.write(f"CoAP server listening on {bind_address}:{bind_port}")

    def _parse_coap_message(self, data):
        # Extract CoAP header information
        #Extracting the first byte to get the version, type, and token length info.
        version_type_token_length = data[0]
        version = (version_type_token_length >> 6) & 0b11
        #Version encoded in the first 2 bits
        type_code = (version_type_token_length >> 4) & 0b0011
        #Type code in the next 2 bits
#       f.write(int(type_code))

        #The next 1 byte is the request/response layer code ->
        method_code_value = struct.unpack('B', data[1:2])[0]
        #The next 2 bytes contain the message ID, which need to be unpacked from the Big-endian binary format it was sent in
        message_id = struct.unpack('!H', data[2:4])[0]

        #So, our URI starts from the 3rd index, or the 4th byte; and extends till we encounter our Payload Marker
        uri_start = 4
        while data[uri_start] != 0xFF:
            uri_start += 1

        # Extract URI and payload
        uri = data[4:data.index(0xFF)].decode('utf-8')
        payload = data[data.index(0xFF) + 1:].decode('utf-8')
        return version, int(type_code), int(method_code_value), message_id, uri, payload

    def _build_coap_response(self, response_code, message_id, uri, payload=None):
        # CoAP Header: Ver(2 bits), Type(2 bits), Token Length(4 bits)
        header = bytearray([0x40 | (1 << 4) | 0x00])
        #Response Code (8 bits)
        header.extend(struct.pack('B', response_code))
        # Message ID (16 bits)
        header.extend(struct.pack('!H', message_id))

        header.extend(uri.encode())
        # Payload Marker
        header.append(0xFF)

        if payload:
            # Payload
            header.extend(payload.encode())
#            header.extend(payload.encode())
        return bytes(header)

    def handle_request(self, data, client_address):
        try:
            version, type_code, method_code_value, message_id, uri, payload = self._parse_coap_message(data)
            # Process the CoAP request as needed
            f.write(f"Received CoAP {self._get_type_name(int(type_code))} request from {client_address}:")
            f.write(f"  The request is for : {self._get_method_name(method_code_value)}")
            f.write(f"  Message ID: {message_id}")
            f.write(f"  URI: {uri}")
            f.write(f"  Payload: {payload}")
        except:
            return
        
        
        response_payload = None
        # Process the CoAP request and prepare the response
        response_code = (2 << 5) | 3   # VALID by default

        if method_code_value == 1:  # GET request
            resource_data = self.resource_repository.get_resource(uri)
            if resource_data is not None:
                response_payload = resource_data
                response_code = (2 << 5) | 5  # Represents 2.05 (69) ==> Content
            else:
                response_code = (4 << 5) | 4  # Not Found
#                response_payload = "Resource not found."

        elif method_code_value == 2:  # POST request
            self.resource_repository.update_resource(uri, payload)
#            response_payload = "Resource created/updated."
            response_code = (2 << 5) | 1        #Represents 2.01 (65)==> Created

        elif method_code_value == 3:  # PUT request
            resource_data = self.resource_repository.get_resource(uri)
            if resource_data is not None:
                self.resource_repository.update_resource(uri, payload)
#                response_payload = "Resource updated."
                response_code = (2 << 5) | 4    #Represents 2.04 ==> Changed
            else:
                response_code = (4 << 5) | 4    #Represents 4.04 ==> Not Found
#               response_payload = "Resource not found."

        elif method_code_value == 4:  # DELETE request
            resource_data = self.resource_repository.get_resource(uri)
            if resource_data is not None:
                self.resource_repository.delete_resource(uri)
#                response_payload = "Resource deleted."
                response_code = (2 << 5) | 2  #Represents 2.02 ==> Deleted
            else:
                response_code = (4 << 5) | 4    #Represents 4.04 ==> Not Found
#               response_payload = "Resource not found."
        else:
            response_code = (4 << 5) | 5   #Represents 4.05 => Method Not allowed
#            response_payload = "Method not allowed for this resource."
        # f.write the contents of the resource repository
        f.write("Contents of Resource Repository:")
        for key, value in self.resource_repository.get_all_resources().items():
            f.write(f"URI: {key}, Data: {value}")

        cloudPayload = {
            'method': self._get_method_name(method_code_value),
            'message_id' : message_id,
            'uri': uri,
            'data': payload
        }

        cloudPayload = json.dumps(cloudPayload) 
        t1 = time.time()
        CoAPServer.server.send_to_cloud(cloudPayload)
        responseCloud = CoAPServer.server.recv_from_cloud()
        t2 = time.time()
        timeElasped = t2 - t1
        f.write(f"Timw: {timeElasped*1000} ms\n")
         
        response = self._build_coap_response(response_code, message_id, uri, response_payload)
        self.server_socket.sendto(response, client_address)

    def _get_method_name(self, method_code_value):
        req_type = {1: "GET", 2: "POST", 3: "PUT", 4: "DELETE"}
        return req_type.get(method_code_value, "Unknown")
    def _get_type_name(self, type_code):
        types = {0: "CON", 1: "NON", 2: "ACK", 3: "RST"}
        return types.get(type_code, "Unknown")

    def run(self):
        try:
            while True:
                data, client_address = self.server_socket.recvfrom(1024)
                request_thread = threading.Thread(target=self.handle_request, args=(data, client_address))
                request_thread.start()
        except KeyboardInterrupt:
            f.write("\nCoAP server stopped.")

if __name__ == "__main__":
    resource_repository = ThreadSafeResourceRepository()
    coap_server = CoAPServer("localhost", 5683, resource_repository)
    coap_server.run()
