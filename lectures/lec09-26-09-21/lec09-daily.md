# Lecture 9 - UDP

## Overview

In Lecture 8, we did a deep dive on socket programming, specifically going through the system calls for socket programming.  In this lecture, we will walk through the two examples from Beej's Guide to Network Programming, finish up our examination of the streaming client and server examples.  We will then explore UDP, examining how it differs from TCP, and why we might want to use it including a look at QUIC which is used for HTTP/3.

## Readings - Lecture 9

* Beej's Guide to Network Programming Links to an external site.
* Chapter 3 - Kurose / Ross

## Optional Reading

* https://blog.cloudflare.com/the-road-to-quic/

## Handouts

* This Overview
* Beej's Streaming Server / Client (last lecture)
* [SocketHelper.cc](./SocketHelper.cc) (see class repo)

## Problem - In-Class

* Suppose we have the following settings
   * MSS = 1k, RTT = 50 ms, CWND_init = 1, SS_Thresh = 16
   * Link Speed = 1.25 Mb/s
   * Transfer data of 50 KB

## Key Points - In-Class - Lecture 9

* What is UDP?
* How does socket programming look different in TCP versus UDP?
* What is QUIC?
* When is it best to use TCP versus UDP?

## Looking Ahead

## Upcoming Deadlines

| **Date** | **Item** | **Topic** |
|---|---|---|
| 09-07 (M) | Reading | Chapter 3 - Transport Layer - Wrap up Today|
| 09-16 (W) | Reading | [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/html/split/) - Chapters 3, 5, 6 - Today |
| 09-21 (M) | Reading | Chapter 4 - Data Plane (for Wednesday) |
| 10-04 (Sun) | Assignment | Coding Project 1 - Part 1 |

The actual assignment entry will be released tonight for Coding Project 1 after all of the respective Canvas groups have been created.
