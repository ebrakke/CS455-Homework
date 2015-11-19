import java.io.*;
import java.util.Arrays;


/**
 * This is the class that students need to implement. The code skeleton is provided.
 * Students need to implement rtinit(), rtupdate() and linkhandler().
 * printdt() is provided to pretty print a table of the current costs for reaching
 * other nodes in the network.
 */ 
public class Node { 
    
    public static final int INFINITY = 9999;
    
    int[] lkcost;		/*The link cost between node 0 and other nodes*/
    int[][] costs;  		/*Define distance table*/
    int nodename;               /*Name of this node*/

	int numNodes = 4;
	String SeparatorLine = "===============================";
    
    /* Class constructor */
    public Node() {
		// Need to initialize the arrays
		costs = new int[numNodes][numNodes];
		lkcost = new int[numNodes];
	}
    
    /* students to write the following two routines, and maybe some others */
    void rtinit(int nodename, int[] initial_lkcost) {
		System.out.printf("Initializing Node %d\n", nodename);
		System.out.println(SeparatorLine);
		// Get which node this currently is
		this.nodename = nodename;

		// Start filling in values for the table
		for (int i = 0; i < numNodes; i++) {
			for (int j = 0; j < numNodes; j++) {
				// Fill in the info for directly connected nodes
				if (i == j) {
					costs[i][j] = initial_lkcost[j];
				} else {
					costs[i][j] = INFINITY;
				}
			}
		}
		// initialize the cost array
		lkcost = initial_lkcost;
		// Send this info to direct neighbors
		for (int i = 0; i < numNodes; i++) {
			// Send the info to directly connected nodes
			if (i == nodename || lkcost[i] == INFINITY) continue;
			sendRoutingInformation(i);
		}
	}
    
    void rtupdate(Packet rcvdpkt) {
		System.out.printf("Updating Node %d From sender %d\n", nodename, rcvdpkt.sourceid);
		System.out.print("Sent ");
		printlk(rcvdpkt.mincost);
		System.out.println(SeparatorLine);
		try {
			int sender = rcvdpkt.sourceid;
			for (int i = 0; i < numNodes; i++) {
				// Update the routing table
				if (rcvdpkt.mincost[i] == INFINITY) {
					costs[i][sender] = INFINITY;
					continue;
				}
				costs[i][sender] = rcvdpkt.mincost[i] + lkcost[sender];
			}
			updateMinCosts(rcvdpkt.sourceid);
		}
		catch (NullPointerException e) {
			System.out.println("Empty packet was sent");
			System.exit(1);
		}

	}

	void updateMinCosts(int sender) {
		// Useful to see if anything has changed
		int[] oldLkCost = Arrays.copyOf(lkcost, lkcost.length);
		int[] poisonArray = new int[numNodes];
		boolean updated = false;
		for (int i = 0; i < numNodes; i++) {
			if (i == nodename) {
				// This cost is always 0
				lkcost[i] = 0;
				continue;
			}
			// Otherwise we need to find the least cost
			int minCost = lkcost[i];
			if (costs[i][sender] < minCost) {
				// The sender is now going to be our next hop to i
				lkcost[i] = costs[i][sender];
				updated = true;
				poisonArray[i] = INFINITY;
			} else {
				// The sender is not our next hop to node i
				poisonArray[i] = lkcost[i];
			}
		}
		printdt();
		if (updated) {
			System.out.println("Link Costs have been updated!");
			System.out.print("Old ");
			printlk(oldLkCost);
			System.out.print("New ");
			printlk(lkcost);
			System.out.println(SeparatorLine);
			sendPoison(poisonArray, sender);
		}
	}
	void sendRoutingInformation(int destination) {
		Packet packet = new Packet(nodename, destination, lkcost);
		System.out.println("Sending information to Node " + destination + " from Node " + nodename);
		printlk(lkcost);
		System.out.println(SeparatorLine);
		NetworkSimulator.tolayer2(packet);
	}

	void sendPoison(int[] poisonArray, int dest) {
		Packet packet = new Packet(nodename, dest, poisonArray);
		System.out.printf("Sending poison packet to Node %d from Node %d\n", dest, nodename);
		printlk(poisonArray);
		System.out.println(SeparatorLine);
		NetworkSimulator.tolayer2(packet);
	}

	void printlk(int[] lk) {
		System.out.printf("Link Costs: ");
		for(int i : lk) {
			System.out.printf("%d ", i);
		}
		System.out.print("\n");
	}

    /* called when cost from the node to linkid changes from current value to newcost*/
    void linkhandler(int linkid, int newcost) {
		// Update the cost
		System.out.printf("\nCost from %d to %d changed to %d\n", nodename, linkid, newcost);
		costs[linkid][linkid] = newcost;
		// Now check to see if we need to update anything
		int minCostToLinkId = INFINITY;
		int nextHop = INFINITY;
		for(int i = 0; i < numNodes; i++) {
			if (costs[linkid][i] < minCostToLinkId) {
				minCostToLinkId = costs[linkid][i];
				nextHop = i;
			}
		}
		// Update lkcost and send poison if necessary
		lkcost[linkid] = INFINITY;
		updateMinCosts(nextHop);
	}


    /* Prints the current costs to reaching other nodes in the network */
    void printdt() {
        switch(nodename) {
	case 0:
	    System.out.printf("                via     \n");
	    System.out.printf("   D0 |    1     2    3 \n");
	    System.out.printf("  ----|-----------------\n");
	    System.out.printf("     1|  %3d   %3d   %3d\n",costs[1][1], costs[1][2],costs[1][3]);
	    System.out.printf("dest 2|  %3d   %3d   %3d\n",costs[2][1], costs[2][2],costs[2][3]);
	    System.out.printf("     3|  %3d   %3d   %3d\n",costs[3][1], costs[3][2],costs[3][3]);
	    break;
	case 1:
	    System.out.printf("                via     \n");
	    System.out.printf("   D1 |    0     2 \n");
	    System.out.printf("  ----|-----------------\n");
	    System.out.printf("     0|  %3d   %3d \n",costs[0][0], costs[0][2]);
	    System.out.printf("dest 2|  %3d   %3d \n",costs[2][0], costs[2][2]);
	    System.out.printf("     3|  %3d   %3d \n",costs[3][0], costs[3][2]);
	    break;
	    
	case 2:
	    System.out.printf("                via     \n");
	    System.out.printf("   D2 |    0     1    3 \n");
	    System.out.printf("  ----|-----------------\n");
	    System.out.printf("     0|  %3d   %3d   %3d\n",costs[0][0], costs[0][1],costs[0][3]);
	    System.out.printf("dest 1|  %3d   %3d   %3d\n",costs[1][0], costs[1][1],costs[1][3]);
	    System.out.printf("     3|  %3d   %3d   %3d\n",costs[3][0], costs[3][1],costs[3][3]);
	    break;
	case 3:
	    System.out.printf("                via     \n");
	    System.out.printf("   D3 |    0     2 \n");
	    System.out.printf("  ----|-----------------\n");
	    System.out.printf("     0|  %3d   %3d\n",costs[0][0],costs[0][2]);
	    System.out.printf("dest 1|  %3d   %3d\n",costs[1][0],costs[1][2]);
	    System.out.printf("     2|  %3d   %3d\n",costs[2][0],costs[2][2]);
	    break;
        }
    }
}
