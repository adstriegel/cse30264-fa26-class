# Lecture 8 - Congestion Control + Socket Programming

## Overview

In Lecture 7, we started in earnest on the material with respect to congestion control.  In today's lecture, we will finish out much of the remaining content on congestion control, and if time allows, also work out an example.  We will then pivot into looking at socket programming, drawing from an example from Beej's Guide to Network Programming.  We will walk through the basics of establishing a socket and then will walk through two specific pieces of code from the client and server perspective.

## Readings - Lecture 8

* Chapter 3
* [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)

## Handouts

* This Overview
* Beej's Streaming Code
   * [Server](./server.c)
   * [Client](./client.c)

## Key Points - In-Class - Lecture 8

* Define / describe: Slow Start, Congestion Avoidance, AIMD, Fast Recovery
* Why does wireless create issues with TCP?
* What is buffer bloat? Why does it matter?
* What is TCP New Reno? CUBIC? BBR?
* How do you initialize a socket?
* How does a client connect to a server?
* How does a server accept new connections from client?
* How do you send / receive data?
* How do you wrap up a connection?

## Refresher - C / Systems Concepts

* How does pointer math work?
* How does typecasting work?
* What is a signal?

## Upcoming Deadlines

| **Date** | **Item** | **Topic** |
|---|---|---|
| 09-07 (M) | Reading | Chapter 3 - Transport Layer |
| 09-16 (W) | Reading | [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/html/split/) - Chapters 3, 5, 6 |
| 09-29 (Sun) | Assignment | Homework 4 - Socket (C) + Short Answer |
| 09-20 (Sun) | Assignment | Group Selection / Repo Sharing |
| 09-21 (M) | Reading | Chapter 4 - Data Plane |

Coding Project 1 will be released on Monday via the class repository.

If you are still looking for a group to join or an additional group member, please wait briefly after class.
