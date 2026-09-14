# Lecture 7 - TCP (Part 2)

## Overview

In Lecture 6, we looked at how TCP delivered reliability moving from the imaginary protocols from last week into sequence numbers, acknowledgments, 3-way handshakes, and the various bits / fields for the protocol.  We will finish off a few things from Part 1 looking at how loss is detected and then we will move onto the congestion control side of TCP, namely how does TCP fairly share network resources?  Whereas flow control deals with how a receiver tells the sender to back off, congestion control is how a sender avoids overwhelming the network and playing nicely with other flows.

## Readings - Lecture 7

* Complete reading Chapter 3 through TCP in the book
* Additional Materials (Optional)
   * [YouTube - Congestion Control Links](https://www.youtube.com/watch?app=desktop&v=rib_ujnMqcs) to an external site. (approx. 12 minutes)
   * https://www.youtube.com/watch?app=desktop&v=rib_ujnMqcs

## Handouts

* This Overview
* [Homework 4](../../homework/hw04/hw04.md)

## Bonus Mateirals

* [Prompt](./discuss-prompt.md) - Default value for SS thresh
* [CoDel - Controlling Queue Delay](https://queue.acm.org/doi/10.1145/2208917.2209336)

## Key Points - In-Class - Lecture 7

* Define / compare: RTT, RTO, Smoothed RTT.
* What is TCP Fast Retransmit?
* What is flow control and why does it matter?
* What is CWND, BDP?
* What is the dumbbell topology?
* What does it mean to be TCP friendly? What is fairness? Jain’s fairness index?
* Compare / contrast: slow start, congestion avoidance, AIMD, SS_thresh
* Why does wireless create issues with TCP?
* What is buffer bloat? Why does it matter?
* What is TCP New Reno? CUBIC? BBR?

## Looking Ahead

* Wednesday - Socket Programming
   * Flip through [Beej's Guide to Socket Programming Links](https://beej.us/guide/bgnet/) to an external site.
* Next Monday - Transport Layer - UDP
   * We will wrap up the transport layer discussing any remaining items on TCP and focus on UDP

## Upcoming Deadlines

| **Date** | **Item** | **Topic** |
|---|---|---|
| 09-07 (M) | Reading | Chapter 3 - Transport Layer |
| 09-16 (W) | Reading | [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/html/split/) - Chapters 3, 5, 6 |
| 09-29 (Sun) | Assignment | Homework 4 - Socket (C) + Short Answer |
| 09-20 (Sun) | Assignment | Group Selection / Repo Sharing |
