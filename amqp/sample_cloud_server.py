import socket

def start_server(host, port):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    while True:
        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Receive and print messages from the client
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # No more data, break the inner loop

            message = data.decode("utf-8")
            print(f"Received message: {message}")

        # Close the client socket
        client_socket.close()

if __name__ == "__main__":
    # Set the host and port
    print('Starting listening server: ')
    host = "127.0.0.1"  # localhost
    port = 7897

    # Start the server
    start_server(host, port)
