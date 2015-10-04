import socket
import sys
import subprocess
from p2client import *

TEST_HOST = 'pcvm2-1.genirack.nyu.edu'
TEST_PORT = 2000
PAYLOAD_SIZE = '1000'
MEASUREMENT_TYPE = 'rtt'
NUMBER_OF_PROBES = '5'


valid_client = ClientSocket(TEST_HOST, TEST_PORT, PAYLOAD_SIZE,  MEASUREMENT_TYPE, NUMBER_OF_PROBES)
invalid_client = ClientSocket(TEST_HOST, TEST_PORT, '256', 'rtt')


def create_setup_message_on_valid_input_passes():
    msg = valid_client.construct_message('s', valid_client.measurement_type, valid_client.num_probes, valid_client.msg_size, valid_client.server_delay)
    return msg == 's rtt 5 1000 0\n'


def create_setup_message_on_invalid_input_fails():
    try:
        invalid_client.construct_message('s', invalid_client.measurement_type, invalid_client.num_probes, invalid_client.msg_size, invalid_client.server_delay)
    except:
        return True


def create_measurement_message_on_valid_input_passes():
    msg = valid_client.construct_message('m', 1)
    return msg == 'm 1 {}\n'.format('a'*1000)


def create_termination_message_on_valid_input_passes():
    msg = valid_client.construct_message('t')
    return msg == 't\n'


def rtt_on_valid_input_succeeds():
    client = ClientSocket('pcvm2-1.genirack.nyu.edu', 2000, 100, 'rtt', 5)
    client.do_protocol()
    return True


def run_tests():
    if not create_setup_message_on_valid_input_passes():
        return "Creating a setup message on valid input failed"
    if not create_setup_message_on_invalid_input_fails():
        return "Creating a setup message on invalid input test failed"
    if not create_measurement_message_on_valid_input_passes():
        return "Creating a measurement message on valid input failed"
    if not create_termination_message_on_valid_input_passes():
        return "Creating a termination message on valid input failed"
    if not rtt_on_valid_input_succeeds():
        return "Error doing valid rtt measurement"
    return "All testing pass!"


if __name__ == '__main__':
    print run_tests()
