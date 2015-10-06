import socket, sys


class ServerSocket:
    def __init__(self, port=58101):
        # Initialize the class variables
        self.port = int(port)
        self.client_socket = None
        self.message = None
        # Create the server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print socket.gethostbyname(socket.gethostname())
            self.sock.bind((socket.gethostbyname(socket.gethostname()), self.port))
            self.sock.listen(1)
        except socket.error:
            raise SetupException

    def accept(self):
        # Accept connections on the socket
        try:
            self.client_socket, address = self.sock.accept()
        except socket.error as e:
            raise AcceptException

    def get_message(self):
        # Get a message from an open port of up to 2048 bytes
        try:
            self.message = self.client_socket.recv(2048)
            print self.message
            self.send_message()
        except socket.error:
            raise ReceiveMessageException

    def send_message(self):
        # Send the message back to the client
        try:
            self.client_socket.send(self.message)
            self.client_socket.close()
        except socket.error:
            raise SendMessageException


class SetupException(Exception):
    def __init__(self):
        self.msg = 'Could not setup the socket'


class AcceptException(Exception):
    def __init__(self):
        self.msg = 'Could not accept the connection'


class ReceiveMessageException(Exception):
    def __init__(self):
        self.msg = 'Could not receive the message'


class SendMessageException(Exception):
    def __init__(self):
        self.msg = 'Could not send the message'


if __name__ == '__main__':
    # Get the port, or set a default if non is supplied
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 58101
    server = ServerSocket(port)
    while 1:
        try:
            server.accept()
            server.get_message()
            server.send_message()
        except AcceptException as e:
            print e.msg
        except ReceiveMessageException as e:
            print e.msg
            server.client_socket.close()
        except SendMessageException as e:
            print e.msg
            server.client_socket.close()
