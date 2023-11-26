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
        else:
            return None

    def update_cache(self, uri, data):
        self.cache[uri] = (time.time(), data)
    def delete_from_cache(self, uri):
        if uri in self.cache:
            del self.cache[uri]

    def show_cache(self):
        return dict(self.cache)


class CoAPClientWithCaching:
    def __init__(self, server_address, server_port, edge_cache):
        self.server_address = server_address
        self.server_port = server_port
        self.edge_cache = edge_cache
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _generate_message_id(self):
        return random.randint(0, 65535)

    def _build_coap_message(self, method, uri, payload=None):
        # Setting first 2 bits to 1 --> Corresponding to Version
        # Setting Message-LAYER field  {type} to NON --> 01 (Next 2 bits)
        # Token length to 0 --> 0000 in the last 4 bits
        header = bytearray([0x40 | (1 << 4) | 0x00])

        method_codes = {
            'GET': 1,
            'POST': 2,
            'PUT': 3,
            'DELETE': 4
        }
        if method.upper() not in method_codes:
            raise ValueError("Invalid CoAP method code")

        code_value = method_codes[method.upper()]
        header.extend(struct.pack('B', code_value))   #Pack the Request/Response Layer code to a 1 byte field

        message_id = self._generate_message_id()
        header.extend(struct.pack('!H', message_id))  # Message ID (16 bits)
        header.extend(uri.encode())  # URI
        header.append(0xFF)  # Payload Marker

        if payload:
            header.extend(payload.encode())  # Payload

        return bytes(header)

    def _parse_coap_response(self, data):
        # Extract CoAP header information
        # Extracting the first byte to get the version, type, and token length info.
        version_type_token_length = data[0]
        version = (version_type_token_length >> 6) & 0b11
        # Version encoded in the first 2 bits
        type_code = (version_type_token_length >> 4) & 0b0011
        # Type code in the next 2 bits
        #       print(int(type_code))

        # The next 1 byte is the request/response layer code ->
        method_code_value = struct.unpack('B', data[1:2])[0]
        # The next 2 bytes contain the message ID, which need to be unpacked from the Big-endian binary format it was sent in
        message_id = struct.unpack('!H', data[2:4])[0]

        # So, our URI starts from the 3rd index, or the 4th byte; and extends till we encounter our Payload Marker
        uri_start = 4
        while data[uri_start] != 0xFF:
            uri_start += 1

        # Extract URI and payload
        uri = data[4:data.index(0xFF)].decode('utf-8')
        payload = data[data.index(0xFF) + 1:].decode('utf-8')
        return version, int(type_code), int(method_code_value), message_id, uri, payload

    def _receive_response(self):
        try:
            response, server_address = self.client_socket.recvfrom(1024)
            version, type_code, method_code_value, message_id, uri, payload = self._parse_coap_response(response)

            if method_code_value == 65:  # Response code 2.01 (Created)
                self.edge_cache.update_cache(uri, payload)
                return None

            elif method_code_value == 68:  # Response code 2.04 (Changed)
                self.edge_cache.update_cache(uri, payload)
                return None

            elif method_code_value == 69:  # Response code 2.05 (Content)
                self.edge_cache.update_cache(uri, payload)
                return None

            elif method_code_value == 66:  #Response code 2.02 (Deleted)
                self.edge_cache.delete_from_cache(uri)
                return None

            elif method_code_value == 132:  #Response code 4.04 (Not Found)
                return None

            elif method_code_value == 133:  #Response code 4.05 (Method Not Allowed)
                return None

        except Exception as e:
            print(f"Error receiving CoAP response: {e}")
            return None


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
            self._receive_response()
#            response, server_address = self.client_socket.recvfrom(1024)
#            self.edge_cache.update_cache(uri, response)
            #response.decode('utf-8')
#            print(f"Received message : {uri}: {message}")
            print("Cache after GET operation:")
            print(self.edge_cache.show_cache())
            return None

        except Exception as e:
            print(f"Error sending/receiving CoAP GET request: {e}")
#        finally:
#           self.client_socket.close()

    def send_post_request(self, uri, payload):
        try:
            message = self._build_coap_message("POST", uri, payload)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
            self._receive_response()
#            response, server_address = self.client_socket.recvfrom(1024)
#            self.edge_cache.update_cache(uri, response)
            print("Cache after POST operation:")
            print(self.edge_cache.show_cache())
            return None
        except Exception as e:
            print(f"Error sending/receiving CoAP POST request: {e}")


    def send_put_request(self, uri, payload):
        try:
            message = self._build_coap_message("PUT", uri, payload)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
#           response, server_address = self.client_socket.recvfrom(1024)
            self._receive_response()
#            self.edge_cache.update_cache(uri, response)
#             print(f"Received response from {server_address}: {response}")
#             return response
            print("Cache after PUT operation:")
            print(self.edge_cache.show_cache())

        except Exception as e:
            print(f"Error sending/receiving CoAP PUT request: {e}")

    def send_delete_request(self, uri):
        try:
            message = self._build_coap_message("DELETE", uri)
            self.client_socket.sendto(message, (self.server_address, self.server_port))
            self._receive_response()

#            self.edge_cache.update_cache(uri, response)
#            print(f"Received response from {server_address}: {response}")
#            return response
            print("Cache after DELETE operation:")
            print(self.edge_cache.show_cache())
            return None

        except Exception as e:
            print(f"Error sending/receiving CoAP DELETE request: {e}")


if __name__ == "__main__":
    edge_cache = EdgeCoAPCache()
    coap_client = CoAPClientWithCaching("localhost", 5683, edge_cache)  # Adjust server address and port
    # for i in range(5):
    #     coap_client.send_get_request("/hello")
    while True:
        # Example: Send POST request
        time.sleep(1)
        coap_client.send_post_request("/roof_sensor", "25.61728, 12.412, 29.111, 81.1920")
        coap_client.send_post_request("/back_sensor", "32.81292, 52.531, 18.019, 07.888")
        time.sleep(1)
        coap_client.send_post_request("/front_sensor", "32.81292, 52.531, 18.019, 07.888")
        # Example: Send PUT request
        time.sleep(1)
        coap_client.send_put_request("/wall_sensor", "32.81292, 52.531, 18.019, 07.888")
        coap_client.send_get_request("/back_sensor")
        # Example: Send DELETE request
        time.sleep(1)
        coap_client.send_delete_request("/telemetry")