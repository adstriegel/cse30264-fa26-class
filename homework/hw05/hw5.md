# Homework 5 - Fall 2026

In this homework, you will be taking a look at a small packet capture file. You can the file here in the class repository.

## Analysis - Wireshark (10 pts)

To answer the following questions, you will need to open up the file in Wireshark and browse through various packets as well as the various analytical tools available in Wireshark (Statistics in the Menu).  Generally though, you should be able to browse the first twenty packets to answer most of the questions.

Answer the following questions:

1. What is the IP address of the client?
2. What is the IP address of the server?
3. How do you know which is the server and which is the client?
4. List the five tuple for the connection from the perspective of the client.
5. What are the raw sequence numbers for each direction (client, server)?
6. What was the MSS set to via the 3-way handshake?
7. How was it set?
8. What is the HTTP version being used for the transfer?
9. What is the user agent for the request?
10. Are there any cookies present (yes or no)?

## Analysis - Coding (5 pts - 2 pts for the pure ACK count, 3 pts for the code)

While Wireshark can be quite useful for looking at information, it cannot always give us the information that we would like.  Tools such as [scapy](https://scapy.net) allow one to open up packet captures programmatically.

Write Python code to do the following:

11. Count how many pure ACKs are sent from the client to the server and the server to the client.  State those numbers.

A pure ACK is a TCP packet that does not have a payload (e.g. no data, the only if the ACK flag being set and / or any relevant TCP Options being present).  Think about how you might detect a pure ACK.

Is there a certain size that you might expect or be able to use as a trigger?  Hint: The Layer 2 information (Ethernet) is usually 14 bytes.  What is the usual size of the IPv4 header?  Can you determine the TCP header size?  Can you look at the IP + TCP header sizes?

12. Paste your code in your answer.

## Submission

Submit your answer as a PDF via Canvas.