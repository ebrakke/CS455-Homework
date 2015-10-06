import sys, socket


class ClientSocket:
    def __init__(self, host, port):
        # Initialize class variables
        self.host = host
        self.port = int(port)
        # Create the socket and connect to the host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        # Connect to socket to the host
        try:
            self.sock.connect((self.host, self.port))
        except socket.error as e:
            print e
            raise ConnectionException

    def send_msg(self, msg='Default Message'):
        # Send a message to the server
        try:
            self.sock.send(msg)  # send a message to the server
        except socket.error:
            raise SendMessageException

    def get_response(self):
        # Get the response from the server and print it
        try:
            res = self.sock.recv(1024)
            print res
            self.sock.close()
        except socket.error:
            raise ReceiveMessageError


class ConnectionException(Exception):
    def __init__(self):
        self.msg = 'Could not connect to the server'


class SendMessageException(Exception):
    def __init__(self):
        self.msg = 'Could not send the message'


class ReceiveMessageError(Exception):
    def __init__(self):
        self.msg = 'Could not receive the message'


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Please enter the host and port number"
        sys.exit(1)
    host, port = sys.argv[1], sys.argv[2]
    try:
        client = ClientSocket(host, port)
        client.connect()
        client.send_msg()
        client.get_response()
        sys.exit(0)
    except ConnectionException as e:
        print e.msg
        sys.exit(1)
    except SendMessageException as e:
        print e.msg
        sys.exit(1)
    except ReceiveMessageError as e:
        print e.msg
        sys.exit(1)
