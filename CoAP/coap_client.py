import socket
import struct
import random
import time

class EdgeCoAPCache:
    def __init__(self):
        self.cache = {}

    def get_from_cache(self, uri):
        if uri in self.cache:
            timestamp, data = self.cache[uri]
            if time.time() - timestamp < 60:
                return data
        return None

    def update_cache(self, uri, data):
        self.cache[uri] = (time.time(), data)

class CoAPClientWithCaching:
    def __init__(self, server_address, server_port, edge_cache):
        self.server_address = server_address
        self.server_port = server_port
        self.edge_cache = edge_cache
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _generate_message_id(self):
        return random.randint(0, 65535)

    def _build_coap_message(self, method, uri, payload=None):

        if (method == "GET"):
            # Creating the Initial Header construct
            header = bytearray([0x40 | (1 << 4) | 0x00])  # CoAP Header
            # Setting first 2 bits to 1 --> Corresponding to Version
            # Setting Message type to GET --> 01 (Next 2 bits)
            # Token length to 0 --> 0000 in the last 4 bits
        elif(method == "POST"):
            header = bytearray([0x40 | (2 << 4) | 0x00])
        elif(method == "PUT"):
            header = bytearray([0x40 | (3 << 4) | 0x00])
        elif(method == "DELETE"):
            header = bytearray([0x40 | (0 << 4) | 0x00])
        else:
            raise ValueError(f"Invalid CoAP method : {method}")

        message_id = self._generate_message_id()
        header.extend(struct.pack('!H', message_id))  # Message ID (16 bits)
        header.extend(uri.encode())  # URI
        header.append(0xFF)  # Payload Marker

        if payload:
            header.extend(payload.encode())  # Payload

        return bytes(header)


#Method to send GET request -->
    ''' Essentially, it retrieves a representation for the information that currently corresponds to
    the resource identified by the request URI. '''
    def send_get_request(self, uri):
        cached_data = self.edge_cache.get_from_cache(uri)

        if cached_data:
            print(f"Found {uri} in edge cache. Returning cached data: {cached_data}")
            return cached_data

        try:
            message = self._build_coap_message("GET", uri)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
            response, server_address = self.client_socket.recvfrom(1024)

            self.edge_cache.update_cache(uri, response)
            #response.decode('utf-8')
            print(f"Received response from {server_address}: {response}")
            return response
            # print(f"Received response from {server_address}: {response.decode('utf-8')}")
            # return response.decode('utf-8')
        except Exception as e:
            print(f"Error sending/receiving CoAP GET request: {e}")
#        finally:
#           self.client_socket.close()

    def get_post_request(self, uri, payload):
        try:
            message = self._build_coap_message("POST", uri, payload)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
            response, server_address = self.client_socket.recvfrom(1024)

            self.edge_cache.update_cache(uri, response)
            print(f"Received response from {server_address}: {response}")
            return response

        except Exception as e:
            print(f"Error sending/receiving CoAP POST request: {e}")


    def send_put_request(self, uri, payload):
        try:
            message = self._build_coap_message("PUT", uri, payload)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
            response, server_address = self.client_socket.recvfrom(1024)

            self.edge_cache.update_cache(uri, response)
            print(f"Received response from {server_address}: {response}")
            return response

        except Exception as e:
            print(f"Error sending/receiving CoAP PUT request: {e}")

    def send_delete_request(self, uri):
        try:
            message = self._build_coap_message("DELETE", uri)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
            response, server_address = self.client_socket.recvfrom(1024)

            self.edge_cache.update_cache(uri, response)
            print(f"Received response from {server_address}: {response}")
            return response

        except Exception as e:
            print(f"Error sending/receiving CoAP DELETE request: {e}")


if __name__ == "__main__":
    edge_cache = EdgeCoAPCache()
    coap_client = CoAPClientWithCaching("localhost", 5683, edge_cache)  # Adjust server address and port
    for i in range(5):
        coap_client.send_get_request("/hello")

    # Example: Send POST request
    coap_client.send_post_request("/roof_sensor", "25.61728, 12.412, 29.111, 81.1920")
    coap_client.send_post_request("/back_sensor", "32.81292, 52.531, 18.019, 07.888")
    coap_client.send_post_request("/front_sensor", "32.81292, 52.531, 18.019, 07.888")
    # Example: Send PUT request
    coap_client.send_put_request("/wall_sensor", "32.81292, 52.531, 18.019, 07.888")

    # Example: Send DELETE request
    coap_client.send_delete_request("/telemetry")