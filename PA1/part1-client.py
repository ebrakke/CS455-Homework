import sys, socket

class ClientSocket:
    def __init__(self, host, port):
        # Create the socket and connect to the host
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
        except socket.error:
            print 'This host does not seem to be accepting connections'
            sys.exit(1)
        except socket.timeout:
            print 'The connection has timed out'
            sys.exit(1)

    def send_msg(self, msg='Default Message'):
        sent = self.socket.send(msg)  # send a message to the server
        if sent != len(msg):
            print 'Entire message was not recieved by server'
        self.get_response() # Wait for the servers response

    def get_response(self):
        # Get the response from the server and print it
        msg = self.socket.recv(2048)

        # Echo the message and exit
        print msg
        self.socket.close()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Please enter the host and port number"
        sys.exit(1)
    host, port = sys.argv[1], int(sys.argv[2])
    client = ClientSocket(host, port)
    client.send_msg()
