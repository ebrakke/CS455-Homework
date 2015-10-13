import sys
import os
from matplotlib import pyplot as plt


def make_plots(sizes, data):
    # Create plots based on the sizes of input and the data supplied
    averages = list()
    for i in sizes:
        averages.append(sum(data.get(i)/len(data)))
    plt.plot(sizes, averages)
    plt.show()


def make_rtt_plot(host, server_delay=False):
    rtt_data = [f for f in os.listdir('.') if 'rtt' in f and host in f and 'sd' not in f]
    if server_delay:
        rtt_data = [f for f in os.listdir('.') if 'rtt' in f and 'sd' in f and host in f]

    # Generate the rtt plots
    size_index = 2 if server_delay else 1
    sizes = sorted([filename.split('_')[size_index] for filename in rtt_data], key=lambda x: int(x))
    rtt_values = dict()
    for f in rtt_data:
        size = f.split('_')[size_index]
        data = open(f).readline().split(', ')
        data = [float(d) for d in data[:-1]]
        avg = sum(data) / len(data)
        rtt_values.setdefault(size, avg)
    plt.figure(1)
    plt.plot(sizes, [rtt_values.get(size) for size in sizes], 'b')
    # plt.ylim([0,2])
    plt.title('Average Round Trip Time with 100 Probes ({})'.format(host))
    if server_delay:
        plt.title('Average RTT with 10 Probes ({}) Server Delay: {} sec'.format(host, server_delay))
    plt.ylabel('Average RTT time (seconds)')
    plt.xlabel('Payload size in bytes')
    plt.show()


def make_tput_plots(host, server_delay=False):
    tput_data = [f for f in os.listdir('.') if 'tput' in f and host in f and 'sd' not in f]
    if server_delay:
        tput_data = [f for f in os.listdir('.') if 'tput' in f and host in f and 'sd' in f]
    print tput_data
    # Generate the rtt plots
    size_index = 2 if server_delay else 1
    sizes = sorted([filename.split('_')[size_index] for filename in tput_data], key=lambda x: int(x))
    tput_values = dict()
    for f in tput_data:
        size = f.split('_')[size_index]
        data = open(f).readline().split(', ')
        data = [float(d) for d in data[:-1]]
        avg = sum(data) / len(data)
        tput_values.setdefault(size, avg)
    plt.figure(1)
    plt.plot(sizes, [tput_values.get(size) for size in sizes], 'ro')
    plt.title('Average Throughput with 100 Probes ({})'.format(host))
    if server_delay:
        plt.title('Average Throughput 10 Probes ({}) Server Delay: {}sec'.format(host, server_delay))
    plt.ylabel('Average Throughput (kbps)')
    plt.xlabel('Payload size in bytes')
    plt.show()


if __name__ == "__main__":
    meas_type, host = sys.argv[1:3]
    server_delay = False
    if len(sys.argv) == 4:
        server_delay = sys.argv[3]
    if meas_type == 'rtt':
        make_rtt_plot(host, server_delay)
    if meas_type == 'tput':
        make_tput_plots(host, server_delay)