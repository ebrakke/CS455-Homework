--------------------
Java Version
--------------------
1. This code is almost a direct translation of the C code
2. The Node class is instantiated 4 times within NetworkSimulator.java as opposed to having a file for each node (node1.c, ..., node4.c)
3. Some methods and variables are made public and static in NetworkSimulator.java to allow the Node class to access them
4. Students need to modify only Node.java. The code skeleton for that class is provided.
5. A Makefile is provided



--------------------
To clean up
--------------------
make clean


--------------------
To compile
--------------------
make all


--------------------
To run
--------------------
java Project3
