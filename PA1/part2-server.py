import socket, sys, time

class Setup404Exception(Exception):
    def __init__(self):
        self.msg = "404 ERROR: Invalid Connection Setup Message"

class MP404Exception(Exception):
    def __init__(self):
        self.msg = "404 ERROR: Invalid Measurement Message"

class ServerSocket:
    def __init__(self, port):
        # Initialize the class variables
        self.measurement_type = None
        self.number_of_probes = None
        self.msg_size = 0
        self.server_delay = 0
        self.client_socket = None

        # Create the server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('', port))
        # Port is probably already in use
        except socket.error as msg:
            print 'Could not establish connection of port {}'.format(port)
            sys.exit(1)

    def listen(self, max_connections=1):
        # Listen to incoming connections
        self.socket.listen(max_connections)

    def accept(self):
        self.client_socket, self.client_address = self.socket.accept()
        if self.client_socket:
            print '{} has connected'.format(self.client_address)
            self.client_socket.settimeout(5)

    def setup_phase(self):
        # Recieve the setup message
        try:
            setup_msg = self.client_socket.recv(1024)
            response = self.parse_msg(setup_msg)
            self.send_message(response)
            # If the message is correct, enter the measurement_phase
            self.measurement_phase()
        except socket.timeout as msg:
            # This means that the client has not sent a valid message
            print 'Connection timeout'
            self.client_socket.close()
        except Setup404Exception as e:
            # Client sent a malformed message
            self.client_socket.send(e.msg)
            self.client_socket.close()

    def measurement_phase(self):
        try:
            for seq in range(0, int(self.number_of_probes)):
                msg = self.client_socket.recv(int(self.msg_size) + 1024)  # Need a buffer at least as big as the payload
                self.parse_msg(msg, seq)
                time.sleep(self.server_delay)  # Wait the specified amount
                self.send_message(msg)
        except MP404Exception as e:
            self.send_message(e.msg)
            self.client_socket.close()

    def send_message(self, msg):
        # Send the message back to the client
        try:
            self.client_socket.send(msg)
        except socket.timeout as msg:
            print 'This socket timed out'
            self.client_socket.close()

    def parse_msg(self, msg, seq=0):
        msg = msg.split(' ')  # Split the message by whitespaces
        if len(msg) == 0: raise Setup404Exception
        # Parse the setup message
        if msg[0] == 's':
            self.validate_message('s', msg)
            # Pull out the information from the message
            self.measurement_type, self.number_of_probes, self.msg_size, self.server_delay = msg[1:]
            return "200 OK: Ready"
        if msg[0] == 'm':
            self.validate_message('m', msg)

    def validate_message(self, phase, msg):
        if phase == 's':
            # Validate setup phase client messages
            return True

        if phase == 'm':
            # Validate the measurement message
            return True


if __name__ == '__main__':
    # Get the port, or set a default if non is supplied
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 58101
    server = ServerSocket(port)
    server.listen()
    while 1:
        server.accept()
        if server.client_socket:
            server.setup_phase()
