import socket, sys

class ServerSocket:
    def __init__(self, port):
        # Create the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', port))

        # Initialize the class variables
        self.message = None
        self.client_socket = None

    def listen(self, max_connections=5):
        # Listen to incoming connections
        self.socket.listen(max_connections)

    def get_message(self):
        # Get a message from an open port of up to 1024 bytes
        self.message = self.client_socket.recv(1024)
        if not self.message:
            self.message = "You did not send me a message"

    def send_message(self):
        # Send the message back to the client
        self.client_socket.send(self.message)
        self.client_socket.close()

if __name__ == '__main__':
    # Get the port, or set a default if non is supplied
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    server = ServerSocket(port)
    server.listen()
    while True:
        (server.client_socket, server.client_address) = server.socket.accept()
        server.get_message()
        server.send_message()
