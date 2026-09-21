// Tracker.cc : Source code for the tracker

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/time.h>

#include <iostream>
using namespace std;

#include "Tracker.h"
#include "utils.h"

Tracker::Tracker()
{
    // Default port is effectively an invalid one
    m_nPort = 0;
    // Nothing in the socket
    m_nSocket = -1;
    m_nNextID = 1;

    m_nLeaseTime = DEFAULT_REGISTER_EXPIRATION;
}

Tracker::~Tracker()
{

}

bool Tracker::initialize (char * pszIP)
{
	struct addrinfo hints, *servinfo, *p;
	int rv;
	socklen_t addr_len;

    /* Double check that port indeed has been initialized */
    if (m_nPort == 0)
    {
        cerr << "Error: Unable to create a server on Port 0.  Make sure to properly initialize" << endl;
        cerr << "  the port setting for the server" << endl;
        return false;
    }

    /* Should check if we are root or just let it roll for a lower-level port? */


    // Set up the hints for UDP, any IP address type
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET; // set to AF_INET to use IPv4
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_flags = AI_PASSIVE; // use my IP

    char szPortString[10];
    snprintf(szPortString, 10, "%d", getPort());

    // getaddrinfo gives us potential avenues for creating the socket that we will
    // use for the tracker

    if ((rv = getaddrinfo(pszIP, szPortString, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return false;
    }

	// loop through all the results and bind to the first we can
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((m_nSocket = socket(p->ai_family, p->ai_socktype,
				p->ai_protocol)) == -1) {
			perror("initialize: socket");
			continue;
		}

        if (bind(m_nSocket, p->ai_addr, p->ai_addrlen) == -1) {
            close(m_nSocket);
            perror("initialize: bind");
            continue;
        }

		break;
	}

	if (p == NULL) {
		fprintf(stderr, "initialize: failed to properly set up socket\n");
		return false;
	}

    // Copy in the respective information for the socket
    memcpy(getAddressInfo(), p->ai_addr, sizeof(struct sockaddr_in));

    // A few notes on addrinfo and sockaddr
    //
    // addrinfo contains lots of information, part of which is a pointer to
    // sockaddr content
    //
    // sockaddr is a "container" that has 16 bytes in total.  It is the same size
    // as a sockaddr_in struct which has enough to hold an IPv4 address as well as
    // the accompanying port and other information

    /*
    struct sockaddr_in {
        short int          sin_family;  // Address family, AF_INET
        unsigned short int sin_port;    // Port number
        struct in_addr     sin_addr;    // Internet address
        unsigned char      sin_zero[8]; // Same size as struct sockaddr
    };
    */

    if(isVerbose())
    {
        dump_sockaddr_in(getAddressInfo());
    }

	freeaddrinfo(servinfo);
    return true;
}

void Tracker::go ()
{
    while(1)
    {
        Message * pRcvMessage;

        pRcvMessage = recvMessage();

        if (pRcvMessage != NULL) {
            switch(pRcvMessage->getType())
            {
                case MSG_TYPE_ECHO:
                    processEcho(pRcvMessage);
                    break;
                case MSG_TYPE_LIST_NODES:
                    processListNodes(pRcvMessage);
                    break;
                case MSG_TYPE_REGISTER:
                    processRegister(pRcvMessage);
                    break;
                default:
                    printf("Unknown message type: %d\n", pRcvMessage->getType());
                    // The client should not be sending these messages to us
                    break;
            }

            delete pRcvMessage;
        }
    }
}

Message * Tracker::recvMessage ()
{
    Message * pMessage;

    socklen_t addr_len;
	struct sockaddr clientAddr;
    int numbytes;

    /* Create a new message object */
    pMessage = new Message ();

	printf("listener: waiting to recvfrom...\n");

	addr_len = sizeof(clientAddr);

	if ((numbytes = recvfrom(getSocket(), pMessage->getData(), pMessage->getMaxLength() , 0,
		(struct sockaddr *)&clientAddr, &addr_len)) == -1) {
		perror("recvfrom");
		exit(1);
	}

    printf("Received a packet from a client of length %d bytes\n", numbytes);

    if(isVerbose())
    {
        dump_sockaddr_in((struct sockaddr_in *) &clientAddr);
    }

    /* Output that we got a packet from that client */
    pMessage->setType(pMessage->getData()[0]);

    /* Save the relevant info */
    pMessage->setLength(numbytes);
    pMessage->recordArrival();

    /* Copy / save the information about the client on the other side */
    memcpy(pMessage->getAddress(), &clientAddr, sizeof(struct sockaddr));

    if(isVerbose())
    {
        pMessage->dumpData();
    }

    return pMessage;
}

bool Tracker::processEcho (Message * pMessageEcho)
{
    Message * pEchoResponse;

    /* The inbound message has the following content:
        Type        1 byte      0x05   Echo
        Length      2 bytes     0x04   Four bytes of data to follow
        Nonce       4 bytes            Randomly generated value in network order
    */

    /* Our task is to reflect the nonce and add in a timestamp that is network
       ordered */

    printf("Processing an echo message from the client");

    uint32_t    theNonce;
    memcpy(&theNonce, pMessageEcho->getData()+3, 4);
    theNonce = ntohl(theNonce);

    printf("  Nonce (Network Order): %d\n", theNonce);

    pEchoResponse = new Message();

    pEchoResponse->setType(MSG_TYPE_ECHO_RESPONSE);
    pEchoResponse->setLength(16);

    // YOLO - Nothing can go wrong directly exposing a pointer and just letting the caller
    //        manipulate the byte array, right?

    /* Set the type */

    pEchoResponse->getData()[0] = MSG_TYPE_ECHO_RESPONSE;

    /* Set the size field */
    uint16_t    theSize;
    theSize = htons(pEchoResponse->getLength());
    memcpy(pEchoResponse->getData()+1, &theSize, 2);

    /* Set the status field - all is well */
    pEchoResponse->getData()[3] = 0;

    /* Copy over the 32 bit nonce data from the initial packet */
    memcpy(pEchoResponse->getData()+4, pMessageEcho->getData()+3, 4);

    /* Let's get the current time */
    struct timeval  theTimeVal;

    /* Who needs return codes? */
    gettimeofday(&theTimeVal, 0);

    printf("  The time at the server is %ld.%d\n", theTimeVal.tv_sec, theTimeVal.tv_usec);

    uint32_t theIntVal;
    theIntVal = htonl(theTimeVal.tv_sec);
    memcpy(pEchoResponse->getData()+8, &theIntVal, 4);

    theIntVal = htonl(theTimeVal.tv_usec);
    memcpy(pEchoResponse->getData()+12, &theIntVal, 4);

    printf("Sending an echo response from the server containg %d bytes\n", pEchoResponse->getLength());

    if(isVerbose())
    {
        pEchoResponse->dumpData();
    }

    sendto(getSocket(), pEchoResponse->getData(), pEchoResponse->getLength(), 0, (struct sockaddr *) pMessageEcho->getAddress(), sizeof(struct sockaddr_in));

    delete pEchoResponse;
    return true;
}

bool Tracker::processRegister (Message * pMessageRegister)
{
    struct timeval  currentTime;
    int nCurrentEntry;

    /* At this point, we know that the message is a registration (0x01) message */

    Message * pMessageRegisterACK;

    /* The format of the registration message should be
     *   1 Byte  - Requested Identifier (0 if unknown, non-zero otherwise)
     *   4 Bytes - IP Address
     *   2 Bytes - Port Number
     *   2 Bytes - Number of Files
     *
     * All content should be in network order (big endian) which would apply to the
     *  IP address, port number, and number of files
    */

    if(isVerbose())
    {
        printf("Displaying the content of the Register Message\n");
        printf("  Actual Length was %d bytes\n", pMessageRegister->getLength());
        printf("  Type: %d\n", pMessageRegister->getData()[0]);

        uint16_t    nMsgLength;

        memcpy(&nMsgLength, pMessageRegister->getData()+1, 2);
        nMsgLength = ntohs(nMsgLength);
        printf("  Stated Length: %d\n", nMsgLength);

        // Requested identifier
        printf("  ID: %d\n", pMessageRegister->getData()[3]);

        // IP address
        printf("  IP: %d.%d.%d.%d\n", pMessageRegister->getData()[4], pMessageRegister->getData()[5], pMessageRegister->getData()[6], pMessageRegister->getData()[7]);

        uint16_t    nPort;
        memcpy(&nPort, pMessageRegister->getData()+8, 2);
        nPort = ntohs(nPort);
        printf("  Port: %d\n", nPort);

        uint16_t    nFiles;
        memcpy(&nFiles, pMessageRegister->getData()+10, 2);
        nFiles = ntohs(nFiles);
        printf("  Files: %d\n", nFiles);
    }


    /* The response message now adds a status field after the length. The length does
       include the status field.
       Overall Format is as follows:
         1 byte  - Type = 0x02
         2 bytes - Length = 17 (0x0011 - big endian format)
         1 byte  - Status = 0 (OK)
         1 byte  - Identifier = Non-zero if assigned / confirmed or zero if there was an issue
         4 bytes - IP Address
         2 bytes - Port
         2 bytes - Number of files
         4 bytes - Expiration of registratin
    */

    pMessageRegisterACK = new Message();

    pMessageRegisterACK->getData()[0] = 0x02;

    /* Set the length appropriately */
    pMessageRegisterACK->setLength(17);

    /* The length is 17 bytes */
    pMessageRegisterACK->getData()[1] = 0x00;
    pMessageRegisterACK->getData()[2] = 0x11;

    /* Skip the status code for now - Byte 3 */
    // Just in case - make it a 1 - something bad??
    pMessageRegisterACK->getData()[3] = 0x01;

    /* Copy over the rest of the original content */
    memcpy(pMessageRegisterACK->getData()+4, pMessageRegister->getData()+3, 9);

    /* Double check / ensure that the registration expiry is zero */
    memset(pMessageRegisterACK->getData()+13,0,4);

    /* Do we have the right size? */
    // For inbound messages here to the server, the length is the actual length as observed
    // as recorded by recvfrom
    if (pMessageRegister->getLength() != 12)
    {
        /* Bad length - note it here on the console */
        cout << "Error: Registration message did wrong count of bytes (Expected 12, had )" << pMessageRegister->getLength() << " bytes" << endl;

        cout << "Dumping the data from the message" << endl;
        pMessageRegister->dumpData();

        /* Status code - nope - this was a bad registration */
        pMessageRegisterACK->getData()[3] = 0x01;

        /* Set the identifier to zero */
        pMessageRegisterACK->getData()[4] = 0x00;

        /* No need to adjust the expiration time - that was already zero'd */
    }
    else
    {
        /* Is this a new registration or a renewal? */
        if(pMessageRegister->getData()[3] == 0x00)
        {
            /* This is a new request (we think) */
            cout << "Detected a new registration (ID was 0)" << endl;

            /* Figure out the next open node ID */
            uint8_t     assignedID;

            assignedID = getNextNodeID();

            /* Create a new node entry from this information */
            Node    theNode;

            theNode.setID(assignedID);

            cout << "  Assigning an ID of " << assignedID << endl;

            uint16_t    theShort;
            uint32_t    theAddress;

            /* Copy over the IP address */
            memcpy(theNode.getIPAddressAsPointer(), pMessageRegister->getData()+4, 4);

            /* Port number */
            memcpy(&theShort, pMessageRegister->getData()+8, 2);
            theShort = ntohs(theShort);
            theNode.setPort(theShort);

            /* Number of files */
            memcpy(&theShort, pMessageRegister->getData()+10, 2);
            theShort = ntohs(theShort);
            theNode.setFiles(theShort);

            /* When did we last see the node? */
            theNode.updateRegistrationTime();

            /* Give it an expiration */

            // What is the current time?
            gettimeofday(&currentTime, 0);

            currentTime.tv_sec += getLeaseTime();

            theNode.setExpirationTime(currentTime);

            m_NodeTable.push_back(theNode);
            nCurrentEntry = m_NodeTable.size()-1;
        }
        else
        {
            cout << "Detected a renewal - detected ID was " << pMessageRegister->getData()[3] << endl;

            // Which node are we?
            nCurrentEntry = findNodeIndexByID(pMessageRegister->getData()[3]);

            if(nCurrentEntry != -1)
            {
                cout << "  Identified the ID as entry " << nCurrentEntry << " in the table" << endl;

                /* When did we last see the node? */
                m_NodeTable[nCurrentEntry].updateRegistrationTime();

                // What is the current time?
                gettimeofday(&currentTime, 0);

                currentTime.tv_sec += getLeaseTime();

                m_NodeTable[nCurrentEntry].setExpirationTime(currentTime);
            }
            else
            {
                cout << "Error: Unable to find a node in the table with ID " << pMessageRegister->getData()[3] << endl;
            }
        }

        if(nCurrentEntry != -1)
        {
            if(isVerbose())
            {
                cout << "This is entry " << nCurrentEntry << " in the table" << endl;
                cout << "  The ID is " << m_NodeTable[nCurrentEntry].getID() << endl;
                cout << "  The expiration is " << m_NodeTable[nCurrentEntry].getExpirationTime().tv_sec << endl;
            }

            pMessageRegisterACK->getData()[3] = 0x00;
            pMessageRegisterACK->getData()[4] = m_NodeTable[nCurrentEntry].getID();

            uint32_t    lSecExpiry;

            /* Get the entry from the table */
            lSecExpiry = m_NodeTable[nCurrentEntry].getExpirationTime().tv_sec;
            /* Apply the appropriate endianness */
            lSecExpiry = htonl(lSecExpiry);

            /* Copy in the network order seconds value for the expiration */
            memcpy(pMessageRegisterACK->getData()+13, &lSecExpiry, 4);
        }
        else
        {
            cout << "Error - Register-ACK message will note a failure" << endl;
            // Had an error - something went bad
            pMessageRegisterACK->getData()[3] = 0x01;
            pMessageRegisterACK->getData()[4] = 0x00;
        }
    }

    // Send the registration ACK message back to the requested client
    printf("Sending a registration ACK from the server containg %d bytes\n", pMessageRegisterACK->getLength());

    if(isVerbose())
    {
        pMessageRegisterACK->dumpData();
    }

    sendto(getSocket(), pMessageRegisterACK->getData(), pMessageRegisterACK->getLength(), 0, (struct sockaddr *) pMessageRegister->getAddress(), sizeof(struct sockaddr_in));

    delete pMessageRegisterACK;
    return true;
}

uint8_t Tracker::getNextNodeID ()
{
    // TODO: Make this more sophisticated for searching (maybe)
    return m_nNextID++;
}

bool Tracker::processListNodes (Message * pMessageListNodes)
{
    if(isVerbose())
    {
        dumpTable();
    }

    /* At this point, we know that the message is a list-nodes (0x03) message */

    Message * pMessageListNodesData;

    /* The format of the list nodes message should be
     *   1 Byte - MaxCount - The maximum number of nodes provided by the tracker
     */

    /* The response message now adds a status field after the length. The length does
    include the status field.
    */

    pMessageListNodesData = new Message();

    pMessageListNodesData->getData()[0] = 0x04;

    /* The length is now variable depending on how many nodes */

    uint8_t     nNodesToShare;

    /* What was the maximum count as requested by the client? */
    nNodesToShare = pMessageListNodes->getData()[3];

    /* Which is bigger - the maximum count from the client or how many nodes we actually have? */
    if (m_NodeTable.size() < nNodesToShare)
    {
        nNodesToShare = (uint8_t) m_NodeTable.size();
    }

    /* Set the status byte */
    pMessageListNodesData->getData()[3] = 0x00;

    /* Reflect back the maximum count */
    pMessageListNodesData->getData()[4] = pMessageListNodes->getData()[3];

    /* State the actual count that is being provided */
    pMessageListNodesData->getData()[5] = nNodesToShare;

    uint16_t    totalLength;

    /* 13 bytes each plus the initial type and length and status and max count / count */
    totalLength = nNodesToShare * 13 + 3 + 1 + 2;
    pMessageListNodesData->setLength(totalLength);

    totalLength = htons(totalLength);

    memcpy(pMessageListNodesData->getData()+1, &totalLength, 2);

    // Offset into the data
    //  Initially is 1 (type) + 2 (length) + 1 (status) + 1 (max count) + 1 (actual count)
    uint16_t theOffset = 1 + 2 + 1 + 1 + 1;

    for(int j=0; j<nNodesToShare; j++)
    {
        theOffset += m_NodeTable[j].constructNodeData(pMessageListNodesData->getData()+theOffset);
    }

    // Send the registration ACK message back to the requested client
    printf("Sending a list-nodes-data from the server containg %d bytes\n", pMessageListNodesData->getLength());

    if(isVerbose())
    {
        pMessageListNodesData->dumpData();
    }

    sendto(getSocket(), pMessageListNodesData->getData(), pMessageListNodesData->getLength(), 0, (struct sockaddr *) pMessageListNodes->getAddress(), sizeof(struct sockaddr_in));

    delete pMessageListNodesData;
    return true;
}

int Tracker::findNodeIndexByID (uint8_t theID)
{
    for (int j=0; j<m_NodeTable.size(); j++)
    {
        if (m_NodeTable[j].getID() == theID)
        {
            return j;
        }
    }

    return -1;
}

void Tracker::dumpTable ()
{
    printf("Tracking Table (%lu entries)\n", m_NodeTable.size());

    for (int j=0; j<m_NodeTable.size(); j++)
    {
        /* ID for the node */
        printf("%3d ", m_NodeTable[j].getID());

        /* IP Address */
        uint8_t * pByte;
        pByte = (uint8_t *) m_NodeTable[j].getIPAddressAsPointer();
        for (int i=0; i<4; i++)
        {
            printf("%3d", pByte[i]);
            if(i<3)
            {
                printf(".");
            }
        }

        /* Port Number */
        printf(" %5d ", m_NodeTable[j].getPort());

        /* Number of files */
        printf("%3d ", m_NodeTable[j].getFiles());

        /* Expiration Time (UTC) */
        // TODO: Make this easier to read?
        printf("%ld\n", m_NodeTable[j].getExpirationTimeAsPointer()->tv_sec);
    }
}