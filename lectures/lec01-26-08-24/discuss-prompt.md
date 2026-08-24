# Prompt / Discussion - Lecture 01 - 08-24-26

## Prompt

What are the most important topics to teach in an undergraduate computer networking class?

## Response (Claude - Opus - 08-22-26)

A few things belong in every version of the course, and then there's a set of choices that separate a good course from a rote one.

**The non-negotiable core**

*Layering and encapsulation* — not as seven memorized boxes but as the actual design idea: why the hourglass narrowed at IP, what you buy with a thin waist, and what it costs you. This is the intellectual spine everything else hangs from.

*Naming, addressing, and indirection* — DNS, IP addressing and CIDR, ARP, NAT. The recurring lesson is that names, addresses, and routes are three different things, and nearly every hard problem in networking is a binding between them.

*Reliable delivery over an unreliable substrate* — sequence numbers, acknowledgments, timers, sliding windows. This is the canonical distributed-systems problem, and students who really understand TCP's state machine understand something that generalizes far beyond networking.

*Congestion control* — AIMD, fairness, the feedback loop. It's the most elegant thing in the field: distributed resource allocation with no central authority and no explicit signaling, and it's why the internet didn't collapse in 1988. Worth spending real time on.

*Routing, and the split between intra- and inter-domain* — distance vector versus link state is the algorithms half, but BGP is the more important lesson: at the internet scale, routing is about policy, money, and trust, not shortest paths.

*Security as a retrofit* — TLS, PKI, and an honest account of the fact that the original architecture assumed a cooperative network. Threat-model thinking matters more than crypto internals here.

**Under-taught, and worth the room**

Performance intuition is the biggest gap I'd flag. Students routinely conflate bandwidth with speed. Bandwidth-delay product, why latency is bounded by physics while throughput isn't, queueing and bufferbloat, Little's Law — this pays off in every systems job they'll ever have.

Measurement and debugging as an actual skill: Wireshark, `traceroute`, `ping`, `curl -v`, `iperf`. Reading a real packet capture of a TLS handshake teaches more than a lecture on it.

And the modern shape of the network: QUIC and HTTP/3, CDNs and the fact that most traffic never traverses the "core," datacenter and cloud networking, middleboxes everywhere, wireless as the default access link. A course that ends at 1998 leaves students unable to reason about the network they'll actually work on.

**Where I'd compress**

Physical-layer modulation and line coding beyond intuition; hand-computed CRC and Hamming distance drills; ATM, token ring, and other historical detail; bit-level header layouts memorized for exams. All of it defensible, none of it worth the weeks it often gets.

**The transferable ideas**

If students remember five things a decade later, I'd want them to be the end-to-end argument, statistical multiplexing, soft state and fate sharing, layering's benefits and its leaks, and the idea that protocols are negotiated contracts between parties who may not trust each other. Saltzer/Reed/Clark is probably the single most valuable reading you can assign.

On delivery: one project where they implement reliable transport over UDP does more than any number of problem sets, because the bugs are the lesson.

Want me to turn this into an actual week-by-week syllabus, or is there a specific tension you're working through — like how much wireless or datacenter material to fit in?
