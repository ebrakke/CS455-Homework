import socket, sys

class ServerSocket:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', port))

    def listen(self, max_connections=5):
        self.socket.listen(max_connections)

    def get_message(self):
        self.message = self.socket.recv(1024)

    def send_message(self):
        self.socket.send(self.message)

if __name__ == '__main__':
    # Get the port, or set a default if non is supplied
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    server = ServerSocket(port)
    server.listen()

    while True:
        (client_socket, address) = server.socket.accept()
        server.get_message()
        if server.message:
            server.send_message()
