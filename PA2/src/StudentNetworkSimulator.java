import java.util.*;
import java.io.*;
import java.util.concurrent.ConcurrentLinkedQueue;

public class StudentNetworkSimulator extends NetworkSimulator
{
    /*
     * Predefined Constants (static member variables):
     *
     *   int MAXDATASIZE : the maximum size of the Message data and
     *                     Packet payload
     *
     *   int A           : a predefined integer that represents entity A
     *   int B           : a predefined integer that represents entity B 
     *
     * Predefined Member Methods:
     *
     *  void stopTimer(int entity): 
     *       Stops the timer running at "entity" [A or B]
     *  void startTimer(int entity, double increment): 
     *       Starts a timer running at "entity" [A or B], which will expire in
     *       "increment" time units, causing the interrupt handler to be
     *       called.  You should only call this with A.
     *  void toLayer3(int callingEntity, Packet p)
     *       Puts the packet "p" into the network from "callingEntity" [A or B]
     *  void toLayer5(String dataSent)
     *       Passes "dataSent" up to layer 5
     *  double getTime()
     *       Returns the current time in the simulator.  Might be useful for
     *       debugging.
     *  int getTraceLevel()
     *       Returns TraceLevel
     *  void printEventList()
     *       Prints the current event list to stdout.  Might be useful for
     *       debugging, but probably not.
     *
     *
     *  Predefined Classes:
     *
     *  Message: Used to encapsulate a message coming from layer 5
     *    Constructor:
     *      Message(String inputData): 
     *          creates a new Message containing "inputData"
     *    Methods:
     *      boolean setData(String inputData):
     *          sets an existing Message's data to "inputData"
     *          returns true on success, false otherwise
     *      String getData():
     *          returns the data contained in the message
     *  Packet: Used to encapsulate a packet
     *    Constructors:
     *      Packet (Packet p):
     *          creates a new Packet that is a copy of "p"
     *      Packet (int seq, int ack, int check, String newPayload)
     *          creates a new Packet with a sequence field of "seq", an
     *          ack field of "ack", a checksum field of "check", and a
     *          payload of "newPayload"
     *      Packet (int seq, int ack, int check)
     *          create a new Packet with a sequence field of "seq", an
     *          ack field of "ack", a checksum field of "check", and
     *          an empty payload
     *    Methods:
     *      boolean setSeqnum(int n)
     *          sets the Packet's sequence field to "n"
     *          returns true on success, false otherwise
     *      boolean setAcknum(int n)
     *          sets the Packet's ack field to "n"
     *          returns true on success, false otherwise
     *      boolean setChecksum(int n)
     *          sets the Packet's checksum to "n"
     *          returns true on success, false otherwise
     *      boolean setPayload(String newPayload)
     *          sets the Packet's payload to "newPayload"
     *          returns true on success, false otherwise
     *      int getSeqnum()
     *          returns the contents of the Packet's sequence field
     *      int getAcknum()
     *          returns the contents of the Packet's ack field
     *      int getChecksum()
     *          returns the checksum of the Packet
     *      int getPayload()
     *          returns the Packet's payload
     *
     */

    /*   Please use the following variables in your routines.
     *   int WindowSize  : the window size
     *   double RxmtInterval   : the retransmission timeout
     *   int LimitSeqNo  : when sequence number reaches this value, it wraps around
     */

    public static final int FirstSeqNo = 0;
    private int WindowSize;
    private double RxmtInterval;
    private int LimitSeqNo;
    
    // Add any necessary class variables here.  Remember, you cannot use
    // these variables to send messages error free!  They can only hold
    // state information for A or B.
    // Also add any necessary methods (e.g. checksum of a String)
    private int currentSeqA;
    private int currentSeqB;
    private boolean isFirstPacket = true;
    private Queue<Packet> bufferedPackets;
    private Queue<Packet> outstandingPackets;
    private int lastAckedPacket;
    private boolean waitingForRx;

    // Stats variables
    private int numOriginalPacketsTrans = 0;
    private int numCorruptPackets;
    private int numRetrans = 0;
    private int numAcksSent = 0;

    // This is the constructor.  Don't touch!
    public StudentNetworkSimulator(int numMessages,
                                   double loss,
                                   double corrupt,
                                   double avgDelay,
                                   int trace,
                                   int seed,
                                   int winsize,
                                   double delay)
    {
        super(numMessages, loss, corrupt, avgDelay, trace, seed);
	WindowSize = winsize;
	LimitSeqNo = winsize+1;
	RxmtInterval = delay;
    }

    
    // This routine will be called whenever the upper layer at the sender [A]
    // has a message to send.  It is the job of your protocol to insure that
    // the data in such a message is delivered in-order, and correctly, to
    // the receiving upper layer.
    protected void aOutput(Message message)
    {
        // Gather all things to make a packet
        String data = message.getData();
        int seq = currentSeqA;
        int checksum = createCheckSum(seq, 0, data);
        Packet packet = new Packet(seq, 0, checksum, data);

        // If we've filled the window, buffer the packets in a queue
        if (outstandingPackets.size() >= WindowSize || bufferedPackets.size() > 0) {
            //System.out.println(packet.toString() + " Added to buffer");
            bufferedPackets.add(packet);
        } else {
            // Restart the timer if there are still packets out there
            if(outstandingPackets.size() > 0) {
                stopTimer(A);
            }
            outstandingPackets.add(packet);
            startTimer(A, RxmtInterval);
            numOriginalPacketsTrans++;
            toLayer3(A, packet);
        }
        currentSeqA = nextSequenceNumber(currentSeqA);
    }
    
    // This routine will be called whenever a packet sent from the B-side 
    // (i.e. as a result of a toLayer3() being done by a B-side procedure)
    // arrives at the A-side.  "packet" is the (possibly corrupted) packet
    // sent from the B-side.
    protected void aInput(Packet packet)
    {
        if(isValidPacket(packet)) {
            if(packet.getAcknum() == lastAckedPacket) {
                // A packet got lost and retransmit
                retransmitOutstandingPackets();
                return;
            }
            // This is a good ACK
            // Remove all received packets from the queue
            Packet p = outstandingPackets.remove();
            while (p.getSeqnum() != packet.getAcknum()) {
                p = outstandingPackets.remove();
            }
            lastAckedPacket = packet.getAcknum();
            if(outstandingPackets.size() == 0){
                stopTimer(A);
            }

            // Send a message from the buffer if there are any
            if(bufferedPackets.size() > 0){
                Packet newPacket = bufferedPackets.remove();
                outstandingPackets.add(newPacket);
                numOriginalPacketsTrans++;
                stopTimer(A);
                startTimer(A, RxmtInterval);
                toLayer3(A, newPacket);
            }
        } else {
            numCorruptPackets++;
        }
    }
    
    // This routine will be called when A's timer expires (thus generating a 
    // timer interrupt). You'll probably want to use this routine to control 
    // the retransmission of packets. See startTimer() and stopTimer(), above,
    // for how the timer is started and stopped. 
    protected void aTimerInterrupt()
    {
        retransmitOutstandingPackets();
        startTimer(A, RxmtInterval);
    }
    
    // This routine will be called once, before any of your other A-side 
    // routines are called. It can be used to do any required
    // initialization (e.g. of member variables you add to control the state
    // of entity A).
    protected void aInit()
    {
        currentSeqA = FirstSeqNo;
        outstandingPackets = new ConcurrentLinkedQueue<Packet>();
        bufferedPackets = new LinkedList<Packet>();
        lastAckedPacket = -1;
    }
    
    // This routine will be called whenever a packet sent from the B-side 
    // (i.e. as a result of a toLayer3() being done by an A-side procedure)
    // arrives at the B-side.  "packet" is the (possibly corrupted) packet
    // sent from the A-side.
    protected void bInput(Packet packet)
    {
        if(isValidPacket(packet)) {
            // This means the first message was corrupt.  Wait for retransmit
            if(packet.getSeqnum() != currentSeqB && isFirstPacket) {
                waitingForRx = true;
                return;
            }
            if(packet.getSeqnum() != currentSeqB && !waitingForRx){
                // A previous packet has been lost
                int prevAck = ((currentSeqA - 1) + LimitSeqNo) % LimitSeqNo;
                Packet ack = createAck(prevAck);
                numRetrans++;
                waitingForRx = true;
                toLayer3(B, ack);
            }
            else {
                // This is the packet we were expecting
                waitingForRx = false;
                toLayer5(packet.getPayload());
                Packet ack = createAck(currentSeqB);
                numAcksSent++;
                toLayer3(B, ack);
                currentSeqB = nextSequenceNumber(currentSeqB);
            }
        } else {
            // The packet was corrupt
            numCorruptPackets++;
        }
    }
    
    // This routine will be called once, before any of your other B-side 
    // routines are called. It can be used to do any required
    // initialization (e.g. of member variables you add to control the state
    // of entity B).
    protected void bInit()
    {
        currentSeqB = FirstSeqNo;
        waitingForRx = false;

    }

    // Use to print final statistics
    protected void Simulation_done()
    {
        System.out.println("done");
        System.out.println("Number of original packets transmitted: " + numOriginalPacketsTrans);
        System.out.println("Number of original ACKS transmitted: " + numAcksSent);
        System.out.println("Number of retransmissions: " + numRetrans);
        System.out.println("Number of corrupt packets: " + numCorruptPackets);
    }

    // My class variables

    // Use this to increment the sequence number
    private int nextSequenceNumber(int currentSeq)
    {
        return (currentSeq + 1) % (LimitSeqNo);
    }

    // Create an ack
    private Packet createAck(int seq) {
        int checkSum = createCheckSum(0, seq, "");
        return new Packet(0, seq, checkSum, "");
    }

    // Create a checksum for a packet
    private int createCheckSum(int seq, int ack, String data)
    {
        int sum = seq + ack;
        if(data.equals("")) {
            return sum;
        }
        for(int i = 0; i < data.length(); i++) {
            sum += (int)data.charAt(i);
        }
        return sum;
    }

    // Validate the packet
    private boolean isValidPacket(Packet packet)
    {
        int seq = packet.getSeqnum();
        int checksum = packet.getChecksum();
        int ack = packet.getAcknum();
        String data = packet.getPayload();

        return checksum == createCheckSum(seq, ack, data);
    }

    // Retransmit the outstanding packets
    private void retransmitOutstandingPackets()
    {
        numRetrans += outstandingPackets.size();
        for(Packet packet: outstandingPackets) {
            toLayer3(A, packet);
        }
    }
}
