# Coding Project 2

In the first coding project, we looked at doing network socket programming, both for TCP as well as UDP.  Fortunately for those cases, we had well-defined firewalls and a largely great campus network to conduct all of our testing meaning that performance largely goes as planned.  However, that is not always the case.  Packets get lost, security protocols have issues, and sometimes we need to troubleshoot why a connection is failing.  While we might dive more deeply into the various logs as part of a network admin or sys admin class, the focus of this second project is to look at a few traces from the perspective of Wireshark as well packages such as scapy which we have already covered briefly in homework assignments.

## 15 pts - Wireshark Exploration

Grab the three Speedtest files from Canvas.  Each of the files involve an [Ookla Speedtest](https://speedtest.net/) captured across three different views of the network:

* One is a connection using a 2.4 GHz link
* One is a connection on a 160 MHz 6 GHz link
* One is a connection across a NordVPN VPN link

Each of the captures had a snaplen or maximum capture length of 100 bytes meaning that only the first 100 bytes of the packets were captured.  All packets were captured using a normal capture meaning that Wireshark by default will save the packets to look like 802.3 or normal Ethernet.  You may notice on your machine that you can sometimes turn on monitor mode but generally Macs tend to be fairly grumpy about enabling such capabilities.  Monitor mode can give your machine the ability to see the control packets for Wi-Fi as well as the data packets.

The packets were also captured on a live Wi-Fi network with a pre-shared key meaning that all of the packets on that particular AP were visible.  That means that packets will be captured from not only the host conducting the speed test but also other devices associated with that same access point.

Open up the files in Wireshark and work with your group to answer the following questions in a `README-Wireshark.md` file in a `cp2` folder in your repository.

* What is the likely IP address of the laptop for each trace?
   * What evidence leads you to believe that? For instance, if you know that a Speedtest was being run, is it likely to move significant amounts of data or only a little bit of data.  What is the menu item in Wireshark that lets you look from a flow-wise perspective?
* Which of the two files do not use a VPN and which file uses a VPN?
   * What evidence leads you to believe that?
   * Think about what is encrypted versus what is visible.
* Are there any ARP packets present?
   * Pick one trace that has at least three ARP packets that is not Professor Striegel's laptop.  Identify three MAC addresses and the likely IP address for that device if possible.
* Can you identify the IP address of the router?
   * Pick one trace and try to figure out the router.  Hint: Use ARP and the MAC identifiers to help you out.
* Are there any DNS packets present?
   * Pick one trace and identify five different host names requested by DNS.
   * What is the primary DNS server being queried? Is it the AP / router? How do you know?
* Identify which trace is which (6 GHz, 2.4 GHz, VPN).
   * Is it possible to directly know from the Wireshark trace if a Wi-Fi link is 6 GHz or 2.4 GHz)?  What might you expect for the 6 GHz link versus the 2.4 GHz link in terms of speed? Your answer could be that it is hard to know but you should justify it.

## 10 pts - scapy

Separate the two non-VPN files.  Write a Python script using `scapy` that does the following:

* Take in as an input the source IP, destination IP, source port, and destination port
* Report the number of packets that match
* Count / report the number of packets with the SYN flag set
* Count / report the number of packets with the RST flag set
* Count / report the number of packets with the FIN flag set
* Count / report the number of packets with any IP options present
* Count / report statistics (mean, median) length of TCP options present

Identify one flow with a substantive number of packets in each of the two Speedtest files.  Report the results of the client (laptop) to the server.  Write your answer in the `README-scapy.md` file.

## Notes

* Everyone should be contributing to each part of the project which means commits of a reasonable size from all group members.  One evaluation item (homework) near the end will be to share an evaluation of your fellow group members and their respective contributions.

* All commits should start with `cp2` as part of their commit message.


* Your code should run on the CSE students machines.  Include any appropriate information in your `README.md` for the virtual environment.

## Submission

Complete the following tasks to submit:

* Make sure you have a `README.md` with any caveats or important notes for grading.
* There are two files for you to create with answers: `README-Wireshark.md` and `README-scapy.md`.  You should also have a Python file that you can choose to name however you see fit.
* Create a final commit with the message `cp2 SUBMISSION`.
* Push your commit to your repository.
* Submit the hash (full or shortened) to the text box via Canvas.

## Bonus Exploration

Open up the fourth file.  This is a capture using Claude with the following prompt:

```
I need to create a tutorial lecture about Wireshark, can you help make me a few slides?
```

Compare and contrast how this file looks versus the other three speedtest traces.  Does it have a similar percentage of UDP versus TCP traffic?
