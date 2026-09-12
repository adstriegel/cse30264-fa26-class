# Discussion Prompt - 09-14-26 - Initial Setting for the Slow Start Threshold

## Prompt

What is the default value for SS_thresh in TCP and why is that the case?

## Response

Yes, this is exactly the problem, and it's well documented. Because cwnd doubles every RTT during slow start, the overshoot when you finally do trigger a congestion signal isn't small — in the very RTT where you cross the bottleneck's capacity, you can be sending up to roughly twice the sustainable rate. That has two nasty consequences. First, when the loss finally happens, it tends to happen to a burst of packets rather than a single one, since the flight size that RTT is so much larger than what the path can drain; multiple losses within one window can push some TCP flavors into a full retransmission timeout rather than a clean fast-recovery, which is a much more expensive event. Second, if there's a deep buffer at the bottleneck (which was extremely common before bufferbloat became a recognized issue), slow start fills that buffer well before any packet is actually dropped — so you get a latency spike building up silently for several RTTs, with the queueing delay ballooning before the sender gets any signal at all that something's wrong.

This is a big part of why several mechanisms were later added specifically to blunt exponential slow-start overshoot rather than relying purely on "grow until it breaks":

Hybrid Start (HyStart, and HyStart++ in more recent CUBIC implementations) watches for an increase in RTT samples during slow start as an implicit early-warning signal of queue buildup, and exits to congestion avoidance (setting ssthresh near the current cwnd) before an actual loss occurs. This is the standard mitigation in Linux's default CUBIC congestion control today.

BBR takes a related but distinct approach: instead of waiting for loss/ECN at all, its startup phase watches for delivery rate to stop increasing meaningfully across a few consecutive RTTs, and treats that plateau as the signal that it's found the bottleneck, exiting startup at that point.

ECN lets a router mark packets as the queue starts to build rather than only dropping them once it's full, so the sender gets a congestion signal earlier in the ramp-up, before the worst-case overshoot.

AQM schemes at the bottleneck itself (CoDel, PIE, fq_codel) are a router-side answer to the same problem: they bound queueing delay and start dropping/marking based on sojourn time rather than just tail-dropping once a large buffer is completely full, which caps how much damage an aggressive slow start can do regardless of what the sender does.

Separately, the receiver's advertised window still puts a hard ceiling on cwnd growth regardless of ssthresh, and standards like RFC 6928 constrain the initial window (rather than ssthresh) to reduce how aggressive the very first RTT is. But none of those touch the core issue you're pointing at — that unbounded exponential growth with no capacity estimate will, by construction, overshoot substantially before the classic loss-based signal arrives. That's precisely the gap HyStart/HyStart++, BBR's startup exit, ECN, and AQM at the bottleneck were each built to close, from different points in the path.

## Prompt - Follow Up

Can you explain the acronyms that you listed above?

## Response

Sure — going through them in the order they came up:

**RFC** (Request for Comments) — the IETF's document series for internet standards and specifications. RFC 5681 and RFC 2581 are the standards documents that define TCP congestion control (slow start, congestion avoidance, fast retransmit/recovery).

**ECN** (Explicit Congestion Notification) — a mechanism (RFC 3168) that lets a router mark a packet's IP header to signal "the queue is building up" instead of dropping the packet outright. The receiver echoes the mark back to the sender via TCP flags, so the sender gets a congestion signal without needing an actual loss.

**HyStart / HyStart++** (Hybrid Start) — an enhancement to slow start, used in CUBIC, that watches for RTT samples starting to rise during slow start (an implicit sign the queue is filling) and exits to congestion avoidance early, before an actual packet is lost. HyStart++ is the refined, standardized version (RFC 9406).

**CUBIC** — the congestion control algorithm that's been the default in Linux for a long time. Its name comes from using a cubic function of elapsed time (rather than a simple linear or purely loss-count-based function) to grow the congestion window during congestion avoidance, which gives it more stable behavior on high-bandwidth, high-latency paths than older algorithms.

**BIC** (Binary Increase Congestion control) — CUBIC's predecessor, which grew cwnd using a binary-search-like approach toward an estimated capacity. CUBIC was designed as a smoother, less aggressive successor to BIC.

**BBR** (Bottleneck Bandwidth and Round-trip propagation time) — a fundamentally different, model-based congestion control algorithm from Google, used increasingly in Linux and at some CDNs. Instead of reacting to loss, it actively estimates the bottleneck's bandwidth and the path's minimum RTT and paces sending based on that model.

**AQM** (Active Queue Management) — the general class of router-side mechanisms that manage queue length proactively (by dropping or marking packets before a buffer is completely full) rather than the older "tail drop" approach of only dropping once the buffer overflows.

**CoDel** (Controlled Delay) — a specific, widely deployed AQM algorithm that targets a bound on how long packets sit in the queue (sojourn time) rather than reacting to queue length in bytes/packets directly.

**PIE** (Proportional Integral controller Enhanced) — another AQM algorithm, developed around the same time as CoDel and with similar delay-control goals, but based on a control-theoretic (proportional-integral) approach to estimating and reacting to queueing delay.

**fq_codel** (Fair Queuing with CoDel) — a Linux queuing discipline that combines per-flow fair queuing (so one flow can't starve others) with CoDel's delay-based AQM on each of those per-flow queues. It's a common default qdisc on Linux and in many home routers.

**cwnd** — congestion window, the sender-side variable that caps how much unacknowledged data TCP is allowed to have in flight, based on its estimate of network capacity.

**rwnd** — receiver's advertised window, the receiver-side cap on in-flight data based on its own buffer space. The sender's actual send window is the minimum of cwnd and rwnd.

**RTT** — round-trip time, the time from sending a packet to receiving its acknowledgment.

**IW** (Initial Window) — the congestion window size a TCP connection starts with, before any RTT feedback. RFC 6928 is the standard that raised the recommended default IW (to around 10 MSS) from the smaller values used in earlier RFCs.
