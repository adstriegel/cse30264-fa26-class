# Discussion Prompt - 09-16-26 - Bufferbloat

## Prompt

How does one avoid bufferbloat and size the buffers correctly for optimizing TCP performance?

## Response

Bufferbloat happens because most network devices—home routers, cable/DSL modems, switches, even some NIC drivers—ship with buffers sized far larger than they need to be, and loss-based TCP (Reno, Cubic) will happily fill any buffer you give it before backing off. The queue sits full for extended periods, RTT balloons from milliseconds to hundreds of milliseconds or even seconds, and interactive traffic (VoIP, gaming, your VR work) suffers even though throughput looks fine on a speed test. The fix has two separable pieces: how big to make the buffer, and what you do with it once packets are sitting in it.

**Buffer sizing theory.** The old rule of thumb, buffer = bandwidth × RTT (the bandwidth-delay product), comes from wanting a single TCP flow to keep the pipe full through one loss-recovery cycle. Appenzeller, Keslassy, and McKeown's "Sizing Router Buffers" (SIGCOMM 2004) showed that for a link carrying many desynchronized long-lived flows, the needed buffer shrinks to roughly RTT × C / √N, since the flows' congestion windows don't all crest and collapse in phase. Router and modem vendors mostly ignored this nuance and just kept adding cheap DRAM, which is a big part of why bufferbloat happened in the first place — it's not that buffers got sized correctly for a bad target, they got wildly oversized for no principled reason at all.

**Why static sizing isn't really the answer.** Trying to hand-pick one buffer size is fragile because the "correct" size depends on flow count, RTT mix, and link rate, all of which change second to second. The actual fix that won consensus is active queue management: instead of sizing the buffer to bound delay, let the buffer be reasonably large (to absorb bursts) but manage its occupancy so sojourn time stays bounded regardless of size.

**CoDel** (Nichols & Jacobson) is the key idea here: it tracks the minimum queueing delay packets have experienced over a sliding interval and starts dropping only when that minimum sojourn time has persistently exceeded a target (defaults: 5 ms target, 100 ms interval). Because it reacts to delay rather than queue length in bytes, it self-tunes to whatever the bottleneck rate actually is, which static byte/packet thresholds (like classic RED) can't do without per-link tuning.

**FQ-CoDel** (RFC 8290, the Linux default qdisc and the basis of OpenWrt's SQM) adds per-flow queuing on top: it hashes packets into subqueues by flow tuple, schedules them round-robin (with a "sparse flow" bonus so new/short flows — DNS lookups, a game's control packets — jump ahead of a saturating bulk transfer), and runs CoDel independently per subqueue. This is why enabling SQM/FQ-CoDel on a home router's WAN interface is the single most effective bufferbloat fix available today — it typically takes a router from an F to an A grade on bufferbloat tests without touching throughput.

**PIE** (Cisco/Bell Labs, used in a lot of DOCSIS 3.1 cable modems) is the other major AQM, using a PI(D)-style controller on estimated queueing latency rather than CoDel's sojourn-time-of-departing-packets approach; conceptually similar goals, different control law.

**ECN and L4S** push this further upstream in the stack. Rather than signaling congestion only via drops (which loss-based TCP interprets slowly, over one RTT of recovery), L4S (RFC 9330 architecture, plus the DualQ Coupled AQM and TCP Prague / scalable congestion control side) marks packets with ECN at a very shallow queue threshold, and scalable congestion controllers react per-ACK/per-mark instead of per-RTT-halving. That's directly relevant if you're weighing L4S vs. best-effort DASH for your grant work — the whole point of L4S is sub-millisecond induced queueing delay at the AQM, versus the tens-of-milliseconds CoDel/FQ-CoDel target, at the cost of needing DualQ deployment and scalable-CC support end to end.

**Endpoint congestion control matters too.** BBR (and successors) estimate bottleneck bandwidth and min-RTT directly via pacing rather than requiring buffer overflow/loss to discover capacity, so a BBR sender induces much less self-inflicted queueing than Cubic even against a dumb buffer. BBRv1 had known fairness problems when competing with loss-based flows at a shared bottleneck; later revisions (BBRv2/v3) work on that. Pairing a modern congestion control at the endpoints with FQ-CoDel/PIE in the network gives you the best of both — neither one alone fully solves it.

**Practically, to size/tune buffers today:**
you don't hand-pick a byte count; you enable an AQM and let its delay target do the sizing work. On Linux, `tc qdisc` with `fq_codel` (target 5ms, interval 100ms are sane defaults — rarely worth changing), or on a router, turn on SQM (OpenWrt calls it exactly that) on the WAN interface set to slightly under your actual sync rate so the bottleneck buffer is the one you control rather than one further upstream in the modem/ISP gear. To verify, use the Waveform Bufferbloat Test, the Cloudflare/DSLReports speed test's bufferbloat grade, or `flent`'s RRUL test if you want the full latency-under-load characterization researchers usually reach for.

Given your L4S grant work, the CoDel paper (Nichols & Jacobson, ACM Queue 2012), the Appenzeller buffer-sizing paper, and RFC 9330/9331 for the L4S architecture and DualQ AQM are probably the most directly citable references if you need them for the proposal.

## Follow Up Prompt

Can you point out a few accessible articles and links on the above mentioned approaches?

## Response

Here's a curated set, going from most foundational/accessible to more technical:

**Bufferbloat, the core concept**
The original explainer, written for a general technical audience by the people who diagnosed the problem: [Bufferbloat: Dark Buffers in the Internet](https://queue.acm.org/detail.cfm?id=2071893) (ACM Queue) and its companion piece [BufferBloat: What's Wrong with the Internet?](https://queue.acm.org/detail.cfm?id=2076798) (a panel discussion format, very readable). The [Bufferbloat.net](https://www.bufferbloat.net/projects/bloat/wiki/Tests_for_Bufferbloat/) project wiki is also a good hub, with a practical page on testing for it. Wikipedia's [Bufferbloat](https://en.wikipedia.org/wiki/Bufferbloat) page is a solid quick-reference summary with good citation trails if you want the primary sources fast.

**CoDel / FQ-CoDel**
Van Jacobson and Kathleen Nichols's own writeup, [Controlling Queue Delay](https://queue.acm.org/detail.cfm?id=2209336) (ACM Queue), is the best entry point — it's written for practitioners, not just theorists, and explains the "good queue vs. bad queue" intuition clearly. The formal spec is [RFC 8289](https://www.rfc-editor.org/rfc/rfc8289.html) if you want the algorithm precisely. For FQ-CoDel specifically plus a walkthrough of the Linux qdisc mechanics, [GeeksforGeeks' CoDel page](https://www.geeksforgeeks.org/computer-networks/controlled-delay-codel-queue-discipline/) is serviceable as a plain-language supplement, and the [Bufferbloat.net CoDel wiki](https://www.bufferbloat.net/projects/codel/wiki/) has implementation notes and FAQ-style clarifications from the people who built it.

**L4S**
The architecture RFC itself is quite readable as RFCs go: [RFC 9330](https://datatracker.ietf.org/doc/rfc9330/). For a lighter, consumer-facing framing of what problem it solves and why it matters, [What Is L4S? Low Latency, Low Loss, Scalable Internet Explained](https://broadbandnow.com/guides/what-is-l4s) (BroadbandNow) is a decent plain-English on-ramp before diving into the RFC.

**BBR**
Adrian Colyer's ["the morning paper" summary of the original BBR paper](https://blog.acolyer.org/2017/03/31/bbr-congestion-based-congestion-control/) is the best short accessible digest of the ACM Queue/CACM BBR paper — it's written specifically to make systems papers approachable. For a more hands-on, example-driven treatment, [TCP BBR: Exploring TCP Congestion Control](https://toonk.io/tcp-bbr-exploring-tcp-congestion-control/index.html) by Andree Toonk walks through real packet captures. The [google/bbr GitHub repo](https://github.com/google/bbr) has Google's own design docs and slide decks linked from the README if you want primary-source detail.

**Testing/measuring it yourself**
The [Bufferbloat.net testing wiki](https://www.bufferbloat.net/projects/bloat/wiki/Tests_for_Bufferbloat/) linked above covers the standard tools (Waveform's test, the Flent RRUL test, DSLReports) with enough detail to pick one for your own measurements.

Sources:
- [Bufferbloat: Dark Buffers in the Internet](https://queue.acm.org/detail.cfm?id=2071893)
- [BufferBloat: What's Wrong with the Internet?](https://queue.acm.org/detail.cfm?id=2076798)
- [Bufferbloat.net — Tests for Bufferbloat](https://www.bufferbloat.net/projects/bloat/wiki/Tests_for_Bufferbloat/)
- [Bufferbloat — Wikipedia](https://en.wikipedia.org/wiki/Bufferbloat)
- [Controlling Queue Delay](https://queue.acm.org/detail.cfm?id=2209336)
- [RFC 8289: Controlled Delay Active Queue Management](https://www.rfc-editor.org/rfc/rfc8289.html)
- [Controlled Delay (CoDel) Queue Discipline — GeeksforGeeks](https://www.geeksforgeeks.org/computer-networks/controlled-delay-codel-queue-discipline/)
- [CoDel Wiki — Bufferbloat.net](https://www.bufferbloat.net/projects/codel/wiki/)
- [RFC 9330: L4S Architecture](https://datatracker.ietf.org/doc/rfc9330/)
- [What Is L4S? — BroadbandNow](https://broadbandnow.com/guides/what-is-l4s)
- [BBR: Congestion-based congestion control — the morning paper](https://blog.acolyer.org/2017/03/31/bbr-congestion-based-congestion-control/)
- [TCP BBR: Exploring TCP Congestion Control — Toonk.io](https://toonk.io/tcp-bbr-exploring-tcp-congestion-control/index.html)
- [google/bbr on GitHub](https://github.com/google/bbr)
