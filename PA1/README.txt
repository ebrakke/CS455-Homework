Erik Brakke
CS 455 - Intro to Networks

##### COMPILATION INSTRUCTIONS #####
Part 1 - Client
Navigate to the folder containing p1client.py
run the command "python p1client.py SERVERADDRESS PORT"
The client will then send the message "Default Message" to a server running at that address on that port

Part 1 - Server
Navigate to folder containing p1server.py
run the command "python p1server.py PORT"
The server will not listen to incoming connections and echo them back to the client

Part 2 - Client
Navigate to folder containing p2client.py
run the command "python p2client.py SERVERADDRESS PORT MEASUREMENT_TYPE NUMBER_OF_PROBES MESSAGE_SIZE [SERVER_DELAY]"
Where MEASUREMENT_TYPE is either 'rtt' or 'tput'
MESSAGE_SIZE is either in Bytes or KB depending on the measurement type
SERVER_DELAY is optional and will default to 0.

The client will the attempt to communicate with the server specified.  It will print out a list of the measurements (rtt or tput)
Then it will write these values to a text file for further analysis

The client will handle any socket errors, and it will handle errors sent back by the server (404 errors)

Part 2 - Server
Navigate to folder containing p2server.py
run "python p2server.py PORT" to have the server start listening
It will then accept 1 connection at a time and attempt to do the protocol with the client
It will catch socket errors and generate its own errors if the client does not specify the correct message
It will let the client know there is an error and then close the connection


##### DESIGN DISCUSSION PART 1 #####
The client is very simple.  It will just send a message to a server and hope that there is a response back.
The client will only receive a 1024 byte message in return, so even if it sends a message that is longer, it won't get any characters over 1024 bytes
The error handling is pretty straight forward.  At each phase, if the socket throws an error, the client with catch it, print a message, and exit

The server is configured pretty similarly to the client.  It will receive and echo messages of 2048 bytes (in case a client sends a longer message)
It is single-threaded and can only accept up to 1 connection at a time. (No connect queue)
It will catch any socket errors, print a message, and then terminate the connection with the client.

Some drawback to this design: Because there is no message format, we can only accept a fixed length message.  If there were some sort of end character
that we could rely on (like a newline), then we could keep receiving messages in chunks until we reached the end character.  There is also no error
communication with the server and client.  If the client does something wrong, the server will just close the connection for no reason.
The server is also not multithreaded, so only one process can happen at a time


##### DESIGN DISCUSSION PART 2 #####
The client is now more complex.  It makes sure that the user supplies correct input in the command line and will not attempt to do the protocol
if any of this is wrong.  It converts KB to B with the conversion of 1KB = 1000B (not 1024).
It then calculates all of the rtt or tput data points depending on which was specified

The server is also more complex.  It will parse the client message to make sure that all of the input is correct and that it is following the protocol.
The server expects that message sizes are always sent in BYTES, (Not KB).  The only time KB is specified is in the client (this seemed to be how the test server did it).

Now there there is a message format, it is easy to send arbitrary length messages to the server and have it be able to recieve and parse all of it.
This is a very big improvement to the previous design

Drawbacks to the design: It is still not multithreaded, so again only one process can take place at a time.  It also only listens to one connections at a time.
This means that if someone else tried to connect while the server was connected with a different process, the second client would get an error
