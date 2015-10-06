#!/usr/bin/python
import socket
import sys
import time


class ServerSocket:
    # CLASS CONSTANTS
    SETUP_PHASE_CLIENT_ERROR = "404 ERROR: Invalid Connection Setup Message\n"
    MEASUREMENT_PHASE_CLIENT_ERROR = "404 ERROR: Invalid Measurement Message\n"
    TERMINATION_PHASE_CLIENT_ERROR = "404 ERROR: Invalid Connection Termination Message\n"
    READY_MESSAGE = "200 OK: Ready\n"
    CLOSING_MESSAGE = "200 OK: Closing Connection\n"
    CLIENT_TIMEOUT_TIME = 10

    def __init__(self, port=58101):
        # Create the server socket with specifications
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None
        self.measurement_type = None
        self.num_probes = None
        self.msg_size = None
        self.server_delay = None

    def initialize(self):
        # Create the server socket on specified host and port
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)  # only accept 1 connection max
        except socket.error:
            raise InitializationException

    def listen(self):
        # Listen for incoming connections
        try:
            self.client_socket, address = self.sock.accept()
            self.client_socket.settimeout(self.CLIENT_TIMEOUT_TIME)  # Make sure the client times out after 5 seconds
            print "New connection from {}".format(address)
        except socket.error:
            raise ListenException

    def setup_phase(self):
        # Run through the setup phase with the client
        try:
            setup_msg = self.get_response()
            self.parse_response('s', setup_msg)
            self.send_message(self.READY_MESSAGE)
        except GetMessageException as e:
            # The server failed to get the entire message
            raise SetupPhaseException
        except ParseMessageException as e:
            raise SetupPhaseException
        except SendMessageException as e:
            raise SetupPhaseException

    def measurement_phase(self):
        # Do the measurement phase of the protocol
        try:
            for i in range(1, int(self.num_probes) + 1):
                res = self.get_response()
                self.parse_response('m', res, i)
                time.sleep(float(self.server_delay))
                self.send_message(res)
        except GetMessageException as e:
            raise MeasurementPhaseException
        except ParseMessageException as e:
            # The message was not correct
            raise MeasurementPhaseException

    def termination_phase(self):
        # Do the termination phase part of the connection
        try:
            res = self.get_response()
            self.parse_response('t', res)
            self.send_message(self.CLOSING_MESSAGE)
        except MessageValidationError as e:
            raise TerminationPhaseException

    def send_message(self, msg):
        self.client_socket.send(msg)

    def get_response(self):
        # Get a message from the client
        try:
            msg = self.client_socket.recv(1024)
            # If the whole message was not received, continue getting it
            while '\n' not in msg:
                msg += self.client_socket.recv(1024)
            return msg
        except socket.timeout:
            # The socket has timed out
            raise GetMessageException

    def parse_response(self, phase, res, *args):
        # pull out the information from the client message
        try:
            if phase == 's':
                self.validate_message('s', res)
                # We know the message is valid, so get the values
                args = res.strip('\n').split(' ')
                self.measurement_type = args[1]
                self.num_probes = args[2]
                self.msg_size = args[3]
                if self.measurement_type == 'tput':
                    self.msg_size = self.msg_size.strip('K') + '000'
                self.server_delay = args[4]

            if phase == 'm':
                seq = args[0]
                self.validate_message('m', res, seq)

            if phase == 't':
                self.validate_message('t', res)

        except MessageValidationError as e:
            raise ParseMessageException

    def validate_message(self, phase, msg, *args):
        # Split the message by whitespaces and validate its contents
        if phase == 's':
            # Valid the setup phase message
            msg_args = msg.strip('\n').split(' ')
            if len(msg_args) != 5:
                raise MessageValidationError
            phase, meas_type, num_probes, msg_size, serv_delay = msg_args
            validation_checks = [
                phase == 's', meas_type in ['rtt', 'tput'], num_probes.isdigit(), \
                (meas_type == 'rtt' and int(msg_size) in [1, 100, 200, 400, 800, 1000]) \
                or (meas_type == 'tput' and int(msg_size) in [1000, 2000, 4000, 8000, 16000, 32000]),
                serv_delay.isdigit()]
            if not all(validation_checks):
                raise MessageValidationError

        if phase == 'm':
            # Validate the measurement phase message
            msg_args = msg.strip('\n').split(' ')
            if len(msg_args) != 3:
                raise MessageValidationError
            phase, seq, payload = msg_args
            actual_seq_num = args[0]
            validation_checks = [phase == 'm', int(seq) == actual_seq_num, len(payload) == int(self.msg_size), \
                                 not (int(seq) > self.num_probes)]
            if not all(validation_checks):
                raise MessageValidationError

        if phase == 't':
            if msg != 't\n':
                raise MessageValidationError

    def close_connection(self):
        self.client_socket.close()

    def do_protocol(self):
        # Run the server through the protocol
        try:
            self.initialize()
        except InitializationException:
            print "Could not start the server"
            sys.exit(1)
        while 1:
            try:
                self.listen()
                # Listen is blocking, so next phase won't fire until someone is connected
                self.setup_phase()  # Run through the setup phase with the client
                self.measurement_phase()  # Do the measurement phase with the client
                self.termination_phase()  # Do the termination phase with the client
                self.close_connection()  # Close the connection with the client
            except ListenException as e:  # Could not listen on the port
                print "Could not listen on port {}".format(self.port)

            except SetupPhaseException as e:  # Send the client the setup phase error
                self.send_message(self.SETUP_PHASE_CLIENT_ERROR)
                self.close_connection()
            except MeasurementPhaseException as e:  # Send the client the measurement phase error
                self.send_message(self.MEASUREMENT_PHASE_CLIENT_ERROR)
                self.close_connection()
            except TerminationPhaseException as e:  # Send the client the termination phase error
                self.send_message(self.TERMINATION_PHASE_CLIENT_ERROR)
                self.close_connection()


# Exceptions
class ParseMessageException(Exception):
    def __init__(self):
        self.msg = "Parsing the message failed"


class ListenException(Exception):
    def __init__(self):
        self.msg = "Could not listen for connections"


class InitializationException(Exception):
    def __init__(self):
        pass


class SetupPhaseException(Exception):
    def __init__(self):
        pass


class MeasurementPhaseException(Exception):
    def __init__(self):
        pass


class TerminationPhaseException(Exception):
    def __init__(self):
        pass


class MessageValidationError(Exception):
    def __init__(self):
        pass


class GetMessageException(Exception):
    def __init__(self):
        pass


class SendMessageException(Exception):
    def __init__(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Please specify PORT"
        sys.exit(1)
    # They specified the right number of argument
    if not sys.argv[1].isdigit():
        print "Please enter a integer for the PORT number"
        sys.exit(1)
    port = int(sys.argv[1])
    server = ServerSocket(port)
    server.do_protocol()
