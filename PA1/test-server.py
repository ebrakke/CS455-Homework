from part2-server import ServerSocket

### Test input ###
server = ServerSocket('localhost', 8000)
valid_setup_msgs = ['s rtt 10 100 0\n', 's tput 10 1000 0\n']
invalid_setup_msgs = ['m rtm 10', 's rtt 10 100']
