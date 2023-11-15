import socket
import struct
import threading


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
    def __init__(self, bind_address, bind_port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((bind_address, bind_port))
        print(f"CoAP server listening on {bind_address}:{bind_port}")

    def _parse_coap_message(self, data):
        # Extract CoAP header information
        #Extracting the first byte to get the version, type, and token length info.
        version_type_token_length = data[0]
        version = (version_type_token_length >> 6) & 0b11
        #Version encoded in the first 2 bits
        type_code = (version_type_token_length >> 4) & 0b0011
        #Type code in the next 2 bits
#       print(int(type_code))
        #The next 2 bytes contain the message ID, which need to be unpacked from the Big-endian binary format it was sent in
        message_id = struct.unpack('!H', data[1:3])[0]

        #So, our URI starts from the 3rd index, or the 4th byte; and extends till we encounter our Payload Marker
        uri_start = 3
        while data[uri_start] != 0xFF:
            uri_start += 1

        # Extract URI and payload
        uri = data[3:data.index(0xFF)].decode('utf-8')
        payload = data[data.index(0xFF) + 1:].decode('utf-8')
        return version, int(type_code), message_id, uri, payload

    def _build_coap_response(self, message_id, response_code, payload=None):
        # CoAP Header: Ver(2 bits), Type(2 bits), Token Length(4 bits)
        header = bytearray([0x40 | (1 << 4) | (response_code >> 5)])
        # Message ID (16 bits)
        header.extend(struct.pack('!H', message_id))
        # Payload Marker
        header.append(0xFF)

        if payload:
            # Payload
            header.extend(payload.encode())
#            header.extend(payload.encode())
        return bytes(header)

    def handle_request(self, data, client_address):
        version, type_code, message_id, uri, payload = self._parse_coap_message(data)

        # Process the CoAP request as needed
        print(f"Received CoAP {self._get_type_name(int(type_code))} request from {client_address}:")
        print(f"  Message ID: {message_id}")
        print(f"  URI: {uri}")
        print(f"  Payload: {payload}")

        # Process the CoAP request and prepare the response
        response_code = 200  # OK by default

        if type_code == 1:  # GET request
            resource_data = self.resource_repository.get_resource(uri)
            if resource_data is not None:
                response_payload = resource_data
            else:
                response_code = 404  # Not Found
                response_payload = "Resource not found."
        elif type_code == 2:  # POST request
            self.resource_repository.update_resource(uri, payload)
            response_payload = "Resource created/updated."
        elif type_code == 3:  # PUT request
            resource_data = self.resource_repository.get_resource(uri)
            if resource_data is not None:
                self.resource_repository.update_resource(uri, payload)
                response_payload = "Resource updated."
            else:
                response_code = 404  # Not Found
                response_payload = "Resource not found."
        elif type_code == 0:  # DELETE request
            resource_data = self.resource_repository.get_resource(uri)
            if resource_data is not None:
                self.resource_repository.delete_resource(uri)
                response_payload = "Resource deleted."
            else:
                response_code = 404  # Not Found
                response_payload = "Resource not found."
        else:
            response_code = 405  # Method Not Allowed
            response_payload = "Method not allowed for this resource."

        response = self._build_coap_response(message_id, response_code, response_payload)
        self.server_socket.sendto(response, client_address)


    def _get_type_name(self, type_code):
        types = {0: "DELETE", 1: "GET", 2: "POST", 3: "PUT"}
        return types.get(type_code, "Unknown")

    def run(self):
        try:
            while True:
                data, client_address = self.server_socket.recvfrom(1024)
                request_thread = threading.Thread(target=self.handle_request, args=(data, client_address))
                request_thread.start()
        except KeyboardInterrupt:
            print("\nCoAP server stopped.")

if __name__ == "__main__":
    coap_server = CoAPServer("localhost", 5683)
    coap_server.run()
