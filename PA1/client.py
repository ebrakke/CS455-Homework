import sys, socket

class ClientSocket:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send_msg(self, msg='Default Message'):
        total_sent = 0
        sent = self.socket.send(msg)
        self.get_response()

    def get_response(self):
        msg = self.socket.recv(1024)
        print msg
        self.close_connection()

    def close_connection(self):
        self.socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Please enter the host and port number"
    host, port = sys.argv[1], int(sys.argv[2])
    client = ClientSocket(host, port)
    client.send_msg()
