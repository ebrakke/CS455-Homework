#!/usr/bin/python
import socket
import sys
import time
from matplotlib import pyplot as plt


class ClientSocket:
    def __init__(self, host_address, port, msg_size, measurement_type, num_probes='10', server_delay='0'):
        # initialize our class variables
        self.host_address = host_address
        self.port = port
        self.msg_size = msg_size
        self.measurement_type = measurement_type
        self.num_probes = num_probes
        self.server_delay = server_delay
        self.trip_times = list()
        try:
            if 'K' in self.msg_size:
                self.msg_size = self.msg_size.strip('K') + '000'
            self.validate_input()
        except ValidationException as e:
            print e.msg
            sys.exit(1)

    def do_protocol(self):
        # Have the client conduct the protocol with the server
        try:
            self.connect()
            self.do_setup_phase()
            self.do_measurement_phase()
            self.do_termination_phase()
            self.print_summary()
        except ConnectionException as e:
            print e.msg
        except SetupPhaseException as e:
            print e.msg
        except MeasurementPhaseException as e:
            print e.msg
        except TerminationPhaseException as e:
            print e.msg
        finally:
            self.close_connection()
            sys.exit(0)

    def connect(self):
        # Create a socket with a host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host_address, int(self.port)))
        except socket.error as e:
            raise ConnectionException('Unable to connect to host: {} on port: {}'.format(self.host_address, self.port))

    def do_setup_phase(self):
        # Conduct the setup phase of the protocol
        try:
            msg = self.construct_message('s')
            self.send_message(msg)
            response = self.get_response()
            self.parse_response('s', response)
        except SendMessageException as e:
            print e.msg
            raise SetupPhaseException('Problem sending message to server')
        except ReceiveMessageException as e:
            print e.msg
            raise SetupPhaseException('Problem receiving a response from the server')

    def do_measurement_phase(self):
        try:
            # Run the experiment for the number of probes requested
            for i in range(1, int(self.num_probes) + 1):
                msg = self.construct_message('m', i)
                start_time = time.time()
                self.send_message(msg)
                response = self.get_response(1024 + int(self.msg_size))
                self.parse_response('m', response)
                stop_time = time.time()
                self.log_trip(start_time, stop_time)
        except SendMessageException as e:
            print e.msg
            raise MeasurementPhaseException('Could not send message to server')
        except ReceiveMessageException as e:
            print e.msg
            raise MeasurementPhaseException('Could not receive message from server')

    def do_termination_phase(self):
        try:
            msg = self.construct_message('t')
            self.send_message(msg)
            response = self.get_response()
            self.parse_response('t', response)
        except SendMessageException as e:
            print e.msg
            raise TerminationPhaseException('Could not send message to server')
        except ReceiveMessageException as e:
            print e.msg
            raise TerminationPhaseException('Could not peacefully terminate connection')

    def close_connection(self):
        self.sock.close()

    def send_message(self, msg):
        # send a message to the client
        self.sock.send(msg)

    def get_response(self, bufsize=1024):
        res = self.sock.recv(bufsize)
        while res.find('\n') == -1:
            res += self.sock.recv(bufsize)
        return res

    def log_trip(self, start_time, end_time):
        # Add the trip time to the list of times
        self.trip_times.append(end_time - start_time)

    def print_summary(self):
        if self.measurement_type == 'tput':
            for i in range(len(self.trip_times)):
                self.trip_times[i] = (float(self.msg_size) / self.trip_times[i]) / 1000  # kbps
        print "The measurements for {} were\n {}".format(self.measurement_type, self.trip_times)

        # Write the output to a file for plotting later
        with open('{}_{}_{}.txt'.format(self.measurement_type, self.msg_size, self.host_address), 'w') as f:
            [f.write('{}, '.format(p)) for p in self.trip_times]
            f.close()

    def construct_message(self, phase, *args):
        # construct a message.  Arguments are already validated
        if phase == 's':
            # If the arguments are valid, turn it into a message
            return 's {} {} {} {}\n'.format(self.measurement_type, self.num_probes, self.msg_size, self.server_delay)

        if phase == 'm':
            payload = 'a' * int(self.msg_size)
            return 'm {} {}\n'.format(args[0], payload)

        if phase == 't':
            return 't\n'

    def validate_input(self):
        # Validates the command line arguments
        if self.measurement_type not in ['rtt', 'tput']:
            raise ValidationException('Not a valid measurment type: {}'.format(self.measurement_type))
        if not self.num_probes.isdigit():
            raise ValidationException('Not a valid number of probes {}'.format(self.num_probes))
        if self.measurement_type == 'rtt' and not self.msg_size.isdigit():
            raise ValidationException('Not a valid message size: {}'.format(self.msg_size))
        if not int(self.msg_size) > 0:
            raise ValidationException('Not a valid message size: {}'.format(self.msg_size))
        if not self.server_delay.isdigit():
            raise ValidationException('Not a valid server delay: {}'.format(self.server_delay))

    @classmethod
    def parse_response(cls, phase, res):
        # Get a message from the server and make sure it's correct
        if phase == 's':
            if res not in ['200 OK: Ready\n', '200 OK:Ready\n']:
                raise ReceiveMessageException('Error establishing the connection')
        if phase == 'm':
            if res == '404 ERROR: Invalid Measurement Message\n':
                raise ReceiveMessageException('Invalid measurement message was sent to server')
        if phase == 't':
            if res != '200 OK: Closing Connection\n':
                raise ReceiveMessageException('Invalid termination message')
        return True


# Exceptions
class ConnectionException(Exception):
    def __init__(self, msg):
        self.msg = msg


class ValidationException(Exception):
    def __init__(self, msg):
        self.msg = msg


class SetupPhaseException(Exception):
    def __init__(self, msg):
        self.msg = msg


class MeasurementPhaseException(Exception):
    def __init__(self, msg):
        self.msg = msg


class TerminationPhaseException(Exception):
    def __init__(self, msg):
        self.msg = 'There was a problem terminating the connection with the server'


class SendMessageException(Exception):
    def __init__(self, msg):
        self.msg = 'There was a problem sending the message to the server'


class ReceiveMessageException(Exception):
    def __init__(self, msg):
        self.msg = msg


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print 'Please supply HOST PORT MEASUREMENT_TYPE, NUMBER_OF_PROBES, MESSAGE_SIZE, [SERVER_DELAY]'
        sys.exit(1)
    argv = sys.argv
    if len (argv) < 7:
        client = ClientSocket(argv[1], argv[2], argv[5], argv[3], argv[4])
    else:
        client = ClientSocket(argv[1], argv[2], argv[5], argv[3], argv[4], argv[6])
    client.do_protocol()