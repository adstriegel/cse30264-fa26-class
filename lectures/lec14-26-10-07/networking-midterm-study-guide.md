# Networking Midterm Study Guide — Fall 26

Oct 4, 2026 · Aaron Striegel

## How to use this guide

Each section maps to the lecture key points: a one-line definition, a small example, and the trap most likely to show up on the exam. Work the problems in the last section by hand before checking the answers.

**Ten things to know cold**

1. Total nodal delay = processing + queueing + transmission (L/R) + propagation (d/s).
2. The five layers (application, transport, network, link, physical) and which header each adds.
3. HTTP request/response format, status codes, and persistent vs non-persistent connections.
4. The 5-tuple: src IP, dst IP, src port, dst port, protocol.
5. TCP 3-way handshake (SYN, SYN-ACK, ACK) and why two messages are not enough.
6. Go-Back-N vs Selective Repeat: what gets retransmitted and what the receiver buffers.
7. Slow start doubles cwnd per RTT; congestion avoidance adds 1 MSS per RTT; loss halves it.
8. BDP = bandwidth × RTT; it is the window you need to keep the pipe full.
9. Subnet math from a prefix length: network address, broadcast address, usable hosts = 2^(32−n) − 2.
10. Forwarding (data plane, per router, nanoseconds) vs routing (control plane, network-wide, seconds).

## 1. Internet basics (Lectures 1–2)

The Internet is a network of networks: hosts at the edge, network devices (routers, switches) in the core, joined by links, all speaking common protocols.

**Core vocabulary**

| Term | Remember it as |
| --- | --- |
| Protocol | Agreed format and order of messages, plus the actions taken on send/receive |
| Packet | A chunk of data plus headers, forwarded independently |
| Forwarding | Moving a packet from a router's input port to the right output port |
| Host | End system running applications (laptop, phone, server) |
| Network device | Router or switch; moves packets, usually no apps |
| Link | Physical medium between two nodes (fiber, copper, radio) |
| Transmission rate | Bits per second a link can push (R) |
| Buffer / queue | Memory where packets wait when the output link is busy; full buffer = drop |

**Circuit vs packet switching**

| | Circuit switching | Packet switching |
| --- | --- | --- |
| Resources | Reserved end-to-end per call | Shared on demand |
| Performance | Guaranteed, no queueing | Variable delay, possible loss |
| Efficiency | Idle capacity is wasted | Statistical multiplexing; supports more bursty users |
| Example | Traditional telephony | The Internet |

Example: a 1 Mbps link, users need 100 kbps when active and are active 10% of the time. Circuit switching supports 10 users. Packet switching can support ~35 users with a very small chance more than 10 are active at once.

**Four types of delay** (per hop)

- Processing: check header, look up output port (microseconds).
- Queueing: wait behind other packets; grows sharply as traffic intensity La/R approaches 1.
- Transmission: L/R — time to push all bits onto the link.
- Propagation: d/s — time for one bit to travel the link (s ≈ 2×10^8 m/s).

Example: L = 1,500 bytes = 12,000 bits, R = 10 Mbps → transmission = 1.2 ms. Link of 2,000 km → propagation = 10 ms.

Trap: transmission depends on packet size and link rate, not distance; propagation depends on distance, not packet size.

**History and service model**

- Telephony: circuit-switched voice network; the Internet originally ran over phone lines, and today voice runs over the Internet (VoIP).
- ARPA (DARPA), part of the U.S. Department of Defense, funded ARPANET, the Internet's predecessor.
- Best effort: IP makes no guarantees on delivery, order, delay, or bandwidth. Reliability is added at the edges (TCP).

**Layers and encapsulation**

| Layer | Unit | Example |
| --- | --- | --- |
| Application | Message | HTTP, SMTP, DNS |
| Transport | Segment (TCP) / datagram (UDP) | TCP, UDP |
| Network | Datagram | IP |
| Link | Frame | Ethernet, Wi-Fi |
| Physical | Bits | Signals on the wire or air |

The ones that matter most in practice: application, transport, network, and link. IP is the narrow waist everything passes through.

Encapsulation: each layer going down adds its header (frame = Ethernet hdr + IP hdr + TCP hdr + HTTP message). Decapsulation: each layer going up strips its header and hands the payload up. Routers decapsulate only up to the network layer.

**Security terms**

- Malware: any malicious software.
- Virus: needs user action to spread (open an attachment).
- Worm: self-propagating, no user action needed.
- DoS: make a resource unavailable by flooding it.
- DDoS: DoS launched from many machines, often a botnet.

## 2. Application layer (Lectures 3–5)

Applications run only on end hosts and talk through sockets; the network core never runs application code.

**End-to-end argument:** put functions (reliability, encryption, app logic) at the endpoints, because only the endpoints can implement them completely. Keep the core simple and fast. This is why HTTP, TLS, and app logic live on hosts, not routers.

**Client/server vs peer-to-peer**

| | Client/server | Peer-to-peer |
| --- | --- | --- |
| Roles | Always-on server with fixed address; clients come and go | Peers are both client and server |
| Scaling | Server capacity is the bottleneck | Self-scaling: each new peer adds upload capacity |
| Management | Simple, centralized | Hard: churn, NAT, trust |
| Example | Web, email | BitTorrent |

**Transport services an app chooses from:** TCP (reliable, ordered, congestion-controlled, connection setup) or UDP (no guarantees, low overhead). The app picks the socket type; transport moves its messages.

**HTTP basics**

HTTP is a stateless, request/response protocol over TCP (port 80; HTTPS on 443).

Request:

```
GET /index.html HTTP/1.1
Host: www.nd.edu
User-Agent: Mozilla/5.0
Accept-Language: en
Connection: keep-alive

```

Response:

```
HTTP/1.1 200 OK
Date: Sun, 04 Oct 2026 18:00:00 GMT
Content-Type: text/html
Content-Length: 4821

<html>...
```

Syntax: request line (method, URL, version) → header lines (Name: value) → blank line → optional body. Methods: GET, POST, HEAD, PUT, DELETE. Status codes: 200 OK, 301 Moved Permanently, 304 Not Modified, 400 Bad Request, 404 Not Found, 500 Server Error.

Key headers: Host, User-Agent, Accept, Connection, Content-Type, Content-Length, Cookie / Set-Cookie, If-Modified-Since, Last-Modified, Cache-Control.

**Cookies** add state to stateless HTTP: the server sends Set-Cookie: id=1678; the browser returns Cookie: id=1678 on later requests.

- Session cookie: deleted when the browser closes.
- Persistent cookie: has an expiry date.
- First-party: set by the site you are visiting.
- Third-party: set by another domain embedded in the page (ads, trackers); used for cross-site tracking.

**Web caching and proxies.** A proxy sits between client and origin and makes requests on the client's behalf. A caching proxy answers repeated requests locally. Conditional GET keeps it fresh: the cache sends If-Modified-Since; the origin replies 304 Not Modified (no body) or 200 with new content.

Example: 60% hit rate → only 40% of requests cross the access link, cutting both link load and average delay.

**Comparing protocols**

| Protocol | Model | Transport / port | Notes |
| --- | --- | --- | --- |
| HTTP | Client/server, pull | TCP 80/443 | Stateless; one object per request |
| FTP | Client/server | TCP 21 control, 20 data | Separate control and data connections; stateful |
| SMTP | Client/server, push | TCP 25 | Server-to-server mail transfer; 7-bit ASCII; persistent |
| BitTorrent | Peer-to-peer | TCP | File split into chunks; tit-for-tat; rarest-first |

**DASH (Dynamic Adaptive Streaming over HTTP).** Video is encoded at several bitrates and cut into chunks of a few seconds. A manifest (MPD) lists them. The client measures throughput and buffer level, then picks the bitrate for each next chunk. All intelligence is at the client; servers are plain HTTP.

**CDN (Content Delivery Network).** Copies of content stored on servers close to users. DNS or anycast steers the client to a nearby server. Two placement styles: enter deep (servers inside access ISPs) or bring home (fewer, larger sites at IXPs).

**HTTP versions**

| Version | Key change | Why it matters |
| --- | --- | --- |
| HTTP/1.0 | One request per TCP connection | 2 RTTs per object |
| HTTP/1.1 | Persistent connections, pipelining | Reuse TCP; still head-of-line blocking |
| HTTP/2 | Binary framing, multiplexed streams, header compression, server push | Many objects on one connection; HOL blocking remains at TCP |
| HTTP/3 | Runs over QUIC (UDP) | Per-stream loss recovery, faster setup |

Non-persistent HTTP: each object costs 2 RTT + transmission (1 RTT TCP setup, 1 RTT request/response).

## 3. Transport layer and TCP basics (Lectures 5–6)

The transport layer provides logical communication between processes; the network layer provides it between hosts.

**Multiplexing / demultiplexing**

- Multiplexing (sender): gather data from many sockets, add transport headers with port numbers.
- Demultiplexing (receiver): use header fields to deliver each segment to the right socket.
- Port: 16-bit number identifying a process/socket on a host. Well-known 0–1023 (HTTP 80, HTTPS 443, SSH 22, SMTP 25, DNS 53); ephemeral ports (e.g., 49152–65535) are picked by the OS for clients.
- Source port: the sender's socket. Destination port: the receiver's socket. In the reply they swap.
- UDP socket is identified by (dst IP, dst port). TCP socket is identified by the full 4-tuple, so a web server on port 80 has a separate socket per client.
- Flow tuple / 5-tuple: (src IP, src port, dst IP, dst port, protocol). Example: (10.0.0.5, 51514, 129.74.12.10, 443, TCP).

**Reliable data transfer protocols**

| | Stop-and-wait | Go-Back-N | Selective Repeat |
| --- | --- | --- | --- |
| Packets in flight | 1 | Up to N | Up to N |
| ACK type | Per packet | Cumulative | Individual per packet |
| Receiver buffers out-of-order? | n/a | No, discards | Yes |
| On loss/timeout | Resend the one packet | Resend that packet and everything after it | Resend only the lost packet |
| Timers | One | One (oldest unACKed) | One per packet |
| Weakness | Low utilization | Wasteful resends | More complex; window ≤ half the sequence space |

Stop-and-wait utilization = (L/R) / (RTT + L/R). Example: L/R = 0.008 ms, RTT = 30 ms → about 0.027% utilization. Pipelining N packets multiplies it by N.

Example: N = 4, packets 0–7, packet 2 lost. GBN resends 2, 3, 4, 5. SR resends only 2; receiver buffers 3–5.

**TCP = Transmission Control Protocol.** Key properties:

- Connection-oriented (handshake before data), point-to-point, full duplex.
- Reliable, in-order byte stream (sequence numbers count bytes, not segments).
- Cumulative ACKs: ACK = next byte expected.
- Flow control and congestion control.

**Segment and MSS.** A segment is TCP's unit: header (20 bytes minimum) plus data. MSS (Maximum Segment Size) is the most application data in one segment, typically 1,460 bytes = 1,500 Ethernet MTU − 20 IP − 20 TCP. It matters because it avoids IP fragmentation and sets the unit cwnd grows by.

**3-way handshake**

1. Client → Server: SYN, seq = x.
2. Server → Client: SYN-ACK, seq = y, ack = x+1.
3. Client → Server: ACK, ack = y+1 (may carry data).

Why three: both sides must pick an initial sequence number and confirm the other received it. Two messages would let the server confirm the client's ISN, but the server's ISN would never be acknowledged, and stale duplicate SYNs could open bogus connections. Teardown uses FIN/ACK in each direction (often 4 segments), then TIME_WAIT.

## 4. TCP timers, flow control, and congestion control (Lectures 7–8)

TCP's sending rate ≈ min(cwnd, rwnd) / RTT: rwnd protects the receiver, cwnd protects the network.

**RTT, smoothed RTT, RTO**

- RTT (SampleRTT): time from sending a segment to receiving its ACK. Noisy; never measured on retransmitted segments (Karn's rule).
- Smoothed RTT: EstimatedRTT = (1 − α)·EstimatedRTT + α·SampleRTT, α = 0.125.
- DevRTT = (1 − β)·DevRTT + β·|SampleRTT − EstimatedRTT|, β = 0.25.
- RTO (retransmission timeout) = EstimatedRTT + 4·DevRTT. On a timeout, RTO doubles (exponential backoff).

Example: EstimatedRTT = 100 ms, DevRTT = 10 ms, new sample 120 ms → EstimatedRTT = 102.5 ms; DevRTT = 0.75·10 + 0.25·20 = 12.5 ms → RTO = 152.5 ms.

**Fast retransmit.** Three duplicate ACKs (four identical ACKs total) mean a segment was likely lost while later ones arrived. Resend it immediately without waiting for the RTO.

**Flow control.** The receiver advertises rwnd (free buffer space) in every ACK. The sender keeps unACKed data ≤ rwnd so it never overflows the receiver. Different from congestion control, which is about the network.

**cwnd and BDP**

- cwnd: congestion window, the sender's own limit on unACKed bytes based on perceived congestion.
- BDP (bandwidth-delay product) = bottleneck rate × RTT = bytes "in the pipe."
- Example: 100 Mbps × 50 ms = 5,000,000 bits = 625 KB. A window smaller than this cannot fill the link; with MSS = 1,460 B that is about 428 segments.

**Dumbbell topology.** Several senders on the left, several receivers on the right, joined by one shared bottleneck link between two routers. It is the standard setup for studying fairness and congestion.

**Fairness**

- Fair: K flows sharing a bottleneck of rate R should each get R/K.
- TCP-friendly: a non-TCP flow (e.g., a UDP video stream) uses no more bandwidth than a TCP flow would under the same loss rate and RTT.
- Jain's fairness index:

$$J = \frac{\left(\sum_{i=1}^{n} x_i\right)^2}{n \sum_{i=1}^{n} x_i^2}$$

J ranges from 1/n (one flow gets everything) to 1 (perfectly equal). Example: throughputs 4, 4, 2 → J = 100 / (3 × 36) = 0.93.

**Congestion control phases**

| Phase | Rule | Growth |
| --- | --- | --- |
| Slow start | cwnd += 1 MSS per ACK | Doubles every RTT (exponential) until ssthresh or loss |
| Congestion avoidance | cwnd += MSS·(MSS/cwnd) per ACK | +1 MSS per RTT (linear) |
| Fast recovery (Reno) | On 3 dup ACKs: ssthresh = cwnd/2, cwnd = ssthresh + 3, inflate per dup ACK | Exits to congestion avoidance on new ACK |
| Timeout | ssthresh = cwnd/2, cwnd = 1 MSS | Back to slow start |

AIMD: additive increase (+1 MSS/RTT), multiplicative decrease (halve on loss). It produces the sawtooth and converges to fairness between flows.

Example: ssthresh = 16, start cwnd = 1. RTTs 1–5: cwnd = 1, 2, 4, 8, 16. Then 17, 18, 19… Loss by 3 dup ACKs at cwnd = 20 → ssthresh = 10, cwnd ≈ 10 (Reno). Loss by timeout → ssthresh = 10, cwnd = 1.

**Variants**

| Variant | Signal | Idea |
| --- | --- | --- |
| Tahoe | Loss | Any loss → cwnd = 1, slow start |
| Reno | Loss | Adds fast recovery for dup-ACK losses |
| NewReno | Loss | Stays in fast recovery through multiple losses in one window (partial ACKs) |
| CUBIC | Loss | cwnd grows as a cubic function of time since last loss; fast far from the old max, flat near it; Linux default |
| BBR | Model | Estimates bottleneck bandwidth and min RTT; paces at that rate rather than filling buffers |

**Bufferbloat.** Oversized router buffers let loss-based TCP fill them before any drop occurs. Result: queues of hundreds of milliseconds, high latency for everyone (gaming, calls) even though throughput looks fine. Fixes: AQM (CoDel, PIE), delay-based or model-based control like BBR, L4S.

**Why wireless hurts TCP.** TCP assumes loss means congestion. On wireless, loss often comes from interference, fading, or handoff, so TCP cuts cwnd needlessly. Link-layer retransmissions add variable delay that inflates RTO, and rates swing quickly.

## 5. Sockets, UDP, and QUIC (Lectures 8–9)

A socket is the door between the application and the transport layer; TCP sockets need a connection, UDP sockets do not.

**TCP socket lifecycle**

| Step | Server | Client |
| --- | --- | --- |
| Initialize | `socket(AF_INET, SOCK_STREAM)` | `socket(AF_INET, SOCK_STREAM)` |
| Set address | `bind(('', 12000))` | (OS picks ephemeral port) |
| Get ready | `listen(backlog)` | — |
| Connect | `accept()` blocks, returns a new connection socket | `connect((host, 12000))` triggers the 3-way handshake |
| Exchange data | `recv()` / `send()` on the connection socket | `send()` / `recv()` |
| Wrap up | `close()` connection socket; keep listening | `close()` sends FIN |

TCP server in Python:

```python
from socket import *
s = socket(AF_INET, SOCK_STREAM)
s.bind(('', 12000))
s.listen(1)
while True:
    conn, addr = s.accept()      # new socket per client
    data = conn.recv(1024)
    conn.send(data.upper())
    conn.close()
```

TCP client in Python:

```python
from socket import *
c = socket(AF_INET, SOCK_STREAM)
c.connect(('localhost', 12000))
c.send(b'hello')
print(c.recv(1024))
c.close()
```

Traps: the listening socket and the accepted socket are different objects. `recv()` may return fewer bytes than asked, since TCP is a byte stream with no message boundaries; `recv()` returning 0 bytes means the peer closed. In C the same calls exist, plus `htons()`/`inet_pton()` for byte order and addresses.

**UDP (User Datagram Protocol).** Connectionless, unreliable, unordered, no congestion or flow control. Header is 8 bytes: src port, dst port, length, checksum. Each send is one message, so boundaries are preserved.

**TCP vs UDP socket code**

| | TCP | UDP |
| --- | --- | --- |
| Socket type | `SOCK_STREAM` | `SOCK_DGRAM` |
| Server calls | bind, listen, accept | bind only |
| Client calls | connect, then send/recv | `sendto(data, (host, port))` / `recvfrom()` |
| Sockets on server | One listening + one per client | One for all clients |
| Delivery | Reliable byte stream | Individual datagrams, may be lost or reordered |

**QUIC.** A transport protocol built in user space on top of UDP (port 443), the basis of HTTP/3. Features: TLS 1.3 built in, 1-RTT setup (0-RTT on resumption), multiple independent streams so one lost packet does not block the others, connection IDs that survive IP changes (Wi-Fi → cellular), and its own congestion control (often CUBIC or BBR).

**When to use which**

- TCP: correctness of every byte matters and some delay is fine — web pages, file transfer, email, SSH, databases.
- UDP: timeliness beats completeness or the exchange is a single query — DNS, VoIP, live video, gaming, DHCP; also as a base for custom protocols like QUIC.
- QUIC: web traffic wanting fast setup and many parallel streams, especially on mobile.

## 6. Network layer: data plane (Lectures 10–13)

The network layer moves datagrams host to host across many routers; every host and router runs it.

**Data plane vs control plane**

| | Data plane | Control plane |
| --- | --- | --- |
| Job | Forwarding: move a packet from input to output port | Routing: compute the paths that fill the tables |
| Scope | Local, per router | Network-wide |
| Speed | Nanoseconds, usually in hardware | Seconds, in software |
| Analogy | Taking the right exit at one interchange | Planning the whole road trip |

**FIB (Forwarding Information Base).** The table a router consults per packet: destination prefix → output interface. Uses longest prefix match.

Example FIB:

| Prefix | Interface |
| --- | --- |
| `11001000 00010111 00010***` | 0 |
| `11001000 00010111 00011000` | 1 |
| `11001000 00010111 00011***` | 2 |
| otherwise | 3 |

Destination `11001000 00010111 00011000 10101010` matches entries for interfaces 1 and 2; the longer match wins → interface 1.

**Scheduling**

- FIFO: one queue, served in arrival order; drop-tail when full.
- Priority queueing: separate queues by class; always serve the highest non-empty class first. Risk: starvation of low priority.
- WFQ (weighted fair queueing): round-robin across classes; class i gets at least w_i / Σw of the link. Example: weights 3, 1 on a 100 Mbps link → 75 and 25 Mbps when both are busy; idle share is reused.

**IPv4 vs IPv6**

| | IPv4 | IPv6 |
| --- | --- | --- |
| Address size | 32 bits (≈4.3 billion) | 128 bits |
| Notation | 129.74.12.10 | 2001:db8::1 |
| Header | 20+ bytes, variable, options | Fixed 40 bytes, extension headers |
| Checksum | Yes | Removed |
| Fragmentation | Routers may fragment | Only the source; routers send ICMPv6 "Packet Too Big" |
| Other | TTL, NAT common | Hop limit, flow label; transition by dual stack or tunneling |

**Fragmentation.** Happens when a datagram is larger than the next link's MTU. IPv4 splits it into fragments with the same ID, an offset (in 8-byte units), and a more-fragments flag; reassembly happens only at the destination.

Example: 4,000-byte datagram (20 header + 3,980 data), MTU 1,500 → three fragments carrying 1,480, 1,480, 1,020 data bytes; offsets 0, 185, 370; MF = 1, 1, 0.

**Subnets.** A subnet is a set of interfaces that can reach each other without a router; they share the high-order bits of their address. Written as a.b.c.d/n (CIDR).

**NAT (Network Address Translation).** A home router maps many private addresses (10/8, 172.16/12, 192.168/16) onto one public IP using a translation table keyed by port: (192.168.1.10, 3345) ↔ (138.76.29.7, 5001). Why it makes life hard: it breaks end-to-end addressing, outside hosts cannot start connections inward (hurts P2P, servers, gaming), it violates layering by rewriting ports, and it needs workarounds such as port forwarding, STUN/TURN, and hole punching.

**DHCP.** Gives a host its IP address, subnet mask, default gateway, and DNS server. Four steps (DORA): Discover (broadcast), Offer, Request, ACK. Runs over UDP (ports 67/68). Addresses are leased. IPv6 equivalent: SLAAC (stateless autoconfiguration from router advertisements) and DHCPv6.

**SDN (Software-Defined Networking).** Separates the control plane into a logically centralized controller that programs the switches' flow tables (e.g., via OpenFlow). What makes it different: match on many header fields (not just destination IP), actions beyond forward (drop, modify, send to controller), and network behavior set by software instead of per-box distributed protocols.

## 7. Network layer: control plane (Lecture 13)

Routing finds good (usually least-cost) paths through a graph of routers and links and turns them into each router's FIB.

**Link state vs distance vector**

| | Link state | Distance vector |
| --- | --- | --- |
| What each router knows | Full topology (flooded link-state advertisements) | Only neighbors' distance estimates |
| Algorithm | Dijkstra, centralized per router | Bellman-Ford, distributed and iterative |
| Equation | Shortest-path tree from source | D_x(y) = min over neighbors v of { c(x,v) + D_v(y) } |
| Messages | O(nE) flooded | Exchanged only with neighbors |
| Convergence | Fast; O(n²) computation | Can be slow; count-to-infinity |
| Robustness | A bad router corrupts only its own table | Errors propagate through the network |
| Protocol | OSPF, IS-IS | RIP |

Distance-vector example: x has links x–y = 2, x–z = 7, y–z = 1. Initially D_x(z) = 7. After y reports D_y(z) = 1, x computes min(7, 2 + 1) = 3, via y.

Count-to-infinity: when a link cost rises, routers may keep pointing at each other and increment slowly. Poisoned reverse (advertise ∞ back to the next hop) helps for two-node loops but not all loops.

**AS, OSPF, BGP**

| | AS | OSPF | BGP |
| --- | --- | --- | --- |
| What it is | Autonomous system: a network under one administration (an ISP, a university) | Intra-AS routing protocol | Inter-AS routing protocol |
| Algorithm | — | Link state (Dijkstra) | Path vector |
| Goal | — | Performance, least cost | Policy and reachability |
| Features | Identified by an AS number | Areas and hierarchy, authentication, multiple equal-cost paths | eBGP between ASes, iBGP within; routes carry AS-PATH and NEXT-HOP; hot-potato routing |

Why two protocols: scale (cannot run Dijkstra over the whole Internet) and administrative autonomy (each AS sets its own policy). BGP route selection: local preference (policy) → shortest AS-PATH → closest NEXT-HOP (hot potato) → tie-breakers. AS-PATH also prevents loops: a router rejects a route already listing its own AS.

## 8. Skills and worked problems (homework and project)

Expect at least one calculation each on subnets, TCP RTT counting, and delay; practice these by hand.

**Identify a five tuple.** Wireshark line: `10.0.0.5:51514 → 129.74.12.10:443 TCP [SYN]`.

- Answer: (10.0.0.5, 51514, 129.74.12.10, 443, TCP). The client is 10.0.0.5 (ephemeral port); the server is HTTPS on 443. The reply flow swaps the IPs and ports.

**Recognize common protocols by port**

| Protocol | Port | Transport |
| --- | --- | --- |
| HTTP / HTTPS | 80 / 443 | TCP (HTTP/3: UDP 443) |
| SSH | 22 | TCP |
| SMTP | 25 (587 submission) | TCP |
| DNS | 53 | UDP (TCP for large) |
| DHCP | 67 / 68 | UDP |

**Extract a subnet from a netmask**

Recipe: find the block size in the "interesting" octet (256 − mask octet), find which block the address falls in, then network = block start, broadcast = next block − 1, usable hosts = 2^(32−n) − 2.

- 192.168.10.77/26 → mask 255.255.255.192, block 64. Network 192.168.10.64, broadcast 192.168.10.127, hosts .65–.126 (62 usable).
- 10.4.200.3/20 → mask 255.255.240.0, block 16 in the third octet. Network 10.4.192.0, broadcast 10.4.207.255, 4,094 usable hosts.
- Same subnet? 172.16.5.9/23 and 172.16.4.200/23: block 2 in the third octet, both fall in 172.16.4.0–172.16.5.255 → yes.

**Count RTTs for a TCP transfer**

Problem: send 15 segments, initial cwnd = 1 MSS, ssthresh large, no loss, transmission time negligible.

- Handshake: 1 RTT.
- Slow start rounds send 1, 2, 4, 8 segments (cumulative 1, 3, 7, 15) → 4 RTTs.
- Total ≈ 5 RTTs (the request rides on the handshake's final ACK).

HTTP object counting: base page + 10 small images.

- Non-persistent, serial: 11 × 2 RTT = 22 RTT.
- Persistent, no pipelining: 2 RTT (base) + 10 × 1 RTT = 12 RTT.
- Persistent with pipelining: 2 RTT + 1 RTT = 3 RTT.

Delay check: 1 MB file over a 10 Mbps link with 20 ms propagation → transmission = 8,000,000 / 10,000,000 = 0.8 s, dwarfing propagation.

**Examine a packet in Wireshark**

- Read the panes top to bottom: Frame → Ethernet → IP → TCP/UDP → application. That is encapsulation in action.
- Useful filters: `ip.addr == 10.0.0.5`, `tcp.port == 443`, `http`, `dns`, `tcp.flags.syn == 1`.
- Things to find: the handshake (SYN, SYN-ACK, ACK), sequence and ACK numbers, window size (rwnd), TTL, HTTP request line and status code.

**Tools**

| Tool | What it does | How it works |
| --- | --- | --- |
| ping | Reachability, RTT, loss | ICMP Echo Request / Echo Reply |
| traceroute | Path and per-hop delay | Sends probes with TTL = 1, 2, 3…; each router that drops one returns ICMP Time Exceeded |
| iperf | Achievable throughput | Client sends TCP or UDP traffic to an iperf server and reports Mbps (UDP also reports jitter and loss) |

**Read basic client/server code**

When shown TCP code (Python or C), be able to say: which side is the server (bind/listen/accept), which call triggers the handshake (connect), which line blocks waiting for a client (accept) or data (recv), what port and address are used, and what happens on close. See the code in Section 5.

Self-check: in the server code, how many sockets exist after two clients connect and are still open? Answer: three — one listening socket plus one connection socket per client.
