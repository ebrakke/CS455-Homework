#!/usr/bin/python
import sys, socket, time

class ClientSocket:
    def __init__(self, host, port, mt, num_p, msg_size, s_delay):
        # Initialize variables
        self.measurement_type = mt
        self.number_of_probes = num_p
        self.msg_size = msg_size
        self.server_delay = s_delay

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

    def setup_phase(self):
        msg = self.construct_msg('s')
        sent = self.socket.send(msg)  # send a message to the server
        response = self.socket.recv(1024)
        if response != '200 OK: Ready':
            print response
            sys.exit(1)
        self.measurement_phase()

    def measurement_phase(self):
        times = list()
        for i in range(0, int(self.number_of_probes)):
            msg = self.construct_msg('m', i)
            start_time = time.time()
            self.socket.send(msg)
            ack = self.socket.recieve(len(msg))
            stop_time = time.time()
            if not ack:
                print 'Server not responding'
                break
            times.append(stop_time - start_time)
        print times

    def construct_msg(self, phase, seq=0):
        # This function will construct messages on behalf of the client
        if phase == 's':
            return 's {} {} {} {}\n'.format(self.measurement_type, self.number_of_probes, self.msg_size, self.server_delay)
        if phase == 'm':
            return 'm {} {}\n'.format(seq, 'a'*int(self.msg_size))


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print "Please enter the host, port, measurement type, number of probes, and message size (optional server delay)"
        sys.exit(1)
    host, port, mt, num_p, msg_size, server_delay = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], 0
    if len(sys.argv) > 6:
        server_delay = sys.argv[5]
    client = ClientSocket(host, port, mt, num_p, msg_size, server_delay)
    client.setup_phase()
