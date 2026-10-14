# Key Points - First Half - Fall 26

## Lecture 1 - 08-24-26

* What is the Internet?
* Define: protocol, packet, forwarding
* Define: host, network device, network link
* Define: transmission rate, buffer, queue
* Compare circuit switching versus packet switching.

## Lecture 2 - 08-26-26

* What are the key types of delay?
* What is telephony? How does it relate to the Internet?
* Which agency drove the original Internet?
* What is best effort?
* What are the layers in the Internet? Which ones matter?
* What is encapsulation / decapsulation?
* Define: malware, virus, worm, DoS, DDoS

## Lecture 3 - 09-01-26

* What is the application layer?
* What does end-to-end argument mean in the context of the application layer?
* Compare and contrast: client / server, peer-to-peer
* What is the transport layer and how does it relate to the application layer?
* What is HTTP? Sketch the basics of the request and the response.

## Lecture 4 - 09-03-26

* What is the general syntax for HTTP requests? What are various headers?
* What are cookies? What are the different types of cookies?
* What is web caching? What does it mean to proxy?
* Compare / contrast: FTP, SMTP, HTTP, BitTorrent

## Lecture 5 - 09-07-26

* Explain DASH.
* Explain what a CDN is.
* What are the different versions of HTTP and why does it matter?
* What is the purpose of the transport layer?
* What does multiplexing / demultiplexing mean?
* What is a port? Source port? Destination port?
* What is a flow tuple?

## Lecture 6 - 09-09-26

* Compare / contrast: Stop and wait, Go Back N, Selective Repeat
* What does TCP stand for?
* What are the key properties of TCP?
* What is a segment? MSS? Why does it matter?
* What is the 3-way handshake for TCP? Why is it 3-way?

## Lecture 7 - 09-14-26

* Define / compare: RTT, RTO, Smoothed RTT.
* What is TCP Fast Retransmit?
* What is flow control and why does it matter?
* What is CWND, BDP?
* What is the dumbbell topology?
* What does it mean to be TCP friendly? What is fairness? Jain’s fairness index?

## Lecture 8 - 09-16-26

* Define / describe: Slow Start, Congestion Avoidance, AIMD, Fast Recovery
* Why does wireless create issues with TCP?
* What is buffer bloat? Why does it matter?
* What is TCP New Reno? CUBIC? BBR?
* How do you initialize a socket?
* How does a client connect to a server?
* How does a server accept new connections from client?
* How do you send / receive data?
* How do you wrap up a connection?

## Lecture 9 - 09-21-26

* What is UDP?
* How does socket programming look different in TCP versus UDP?
* What is QUIC?
* When is it best to use TCP versus UDP?

## Lecture 10 - 09-23-26

* What is the data plane versus the control plane?
* What is the network layer?
* Compare / contrast: IPv4 vs. IPv6
* What is the difference between forwarding versus routing?
* Compare / contrast: FIB, priority queueing, WFQ
* What is a FIB?

## Lecture 11 - 09-28-26

* Compare / contrast: FIFO, priority queueing, WFQ
* What is the difference between forwarding versus routing?
* What is the data plane versus the control plane?
* Compare / contrast: IPv4 vs. IPv6
* What is a FIB?
* What is fragmentation / why does it occur?

## Lecture 12 - 10-01-26

* Data Plane
   * What is a subnet?
   * What is NAT? Why does it make our life hard?
   * What is DHCP? What is the v6 equivalent?

## Lecture 13 - 10-05-26

* Data Plane
   * What is SDN? What makes it “different”?
* Control Plane
   * What is routing? What purpose does it serve?
   * Compare / contrast: link state, distance vector.
   * Compare / contrast: AS, OSPF, BGP.

## General Skills / Tools - Homework, Project

* Identify a five tuple
* Identify the most common application layer protocols - HTTP, SMTP, SSH
* Extract a subnet from a netmask
* Derive how many RTTs it would take to transfer data via TCP
* Examine a packet via Wireshark
* What is: ping, traceroute, iperf
* Read / understand code for a basic TCP client - Python or C
* Read / understand code for a basic TCP server - Python or C
