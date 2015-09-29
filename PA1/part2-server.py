import socket, sys

class ServerSocket:
    def __init__(self, port):
        # Initialize the class variables
        self.message = None
        self.client_socket = None
        # Create the server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('', port))
        # Port is probably already in use
        except socket.error as msg:
            print 'Could not establish connection of port {}'.format(port)
            sys.exit(1)

    def listen(self, max_connections=5):
        # Listen to incoming connections
        self.socket.listen(max_connections)

    def accept(self):
        self.client_socket, self.client_address = self.socket.accept()
        if self.client_socket:
            print '{} has connected'.format(self.client_address)
            self.client_socket.settimeout(5)

    def get_message(self):
        # Get a message from an open port of up to 2048 bytes
        try:
            self.message = self.client_socket.recv(2048)
            self.send_message()
        except socket.timeout as msg:
            # This means that the client has not sent a valid message
            print 'This socket has timed out recieving the message'
            # Tell the client his message was inavlid and close the connection
            self.client_socket.send('You did not send me a valid message')
            self.client_socket.close()

    def send_message(self):
        # Send the message back to the client
        try:
            self.client_socket.send(self.message)
        except socket.timeout as msg:
            print 'This socket timed out'
        finally:
            self.client_socket.close()

if __name__ == '__main__':
    # Get the port, or set a default if non is supplied
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 58101
    server = ServerSocket(port)
    server.listen()
    while 1:
        server.accept()
        server.get_message()
