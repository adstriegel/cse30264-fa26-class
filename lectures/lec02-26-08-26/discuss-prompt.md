# Prompt / Discussion - Lecture 02 - 08-26-26

## Prompt

What are the key points for a junior software engineer to know about the history of the Internet?

## Response (Claude - Opus - 08-24-26)

A few threads matter most, and they're the ones that explain why today's systems behave the way they do.

**It was built for survival, not for you.** ARPANET (1969) and the packet-switching ideas behind it came out of a world where the design goal was that the network keep working when parts of it fail. That's why IP is *best-effort*: routers can drop packets, reorder them, and duplicate them, and that's considered normal operation. Every reliability guarantee you rely on is bolted on above that layer. If you've ever wondered why distributed systems are hard, this is the root cause — the substrate promises almost nothing.

**TCP/IP won because it was end-to-end.** The 1974 Cerf/Kahn design and the January 1, 1983 "flag day" cutover established the key architectural bet: the network stays dumb, the endpoints stay smart. The end-to-end principle is why you could invent a new protocol on top of TCP this afternoon without asking anyone's permission, and it's the reason the internet absorbed the web, video streaming, and everything since without being redesigned. It's also why middleboxes, NATs, and deep packet inspection feel like violations — they are, architecturally.

**Congestion collapse taught the internet manners.** In 1986 the network essentially melted; throughput between LBL and Berkeley fell from 32 kbit/s to 40 bit/s. Van Jacobson's congestion control (slow start, AIMD) fixed it, and it's *voluntary* — the network doesn't enforce it, endpoints cooperate. That's a useful mental model: much of the internet works because everyone agreed to back off, not because anything stops them.

**DNS made it human-usable, and it's a cache with a global namespace.** Before 1983 there was a single HOSTS.TXT file that someone maintained by hand. DNS replaced it with a hierarchical, delegated, aggressively cached system. Practical consequence for you: DNS is eventually consistent, TTLs matter, and "it's always DNS" is a joke because caching and delegation produce failures that look like anything but DNS.

**The web was a layer on top, and it was late.** Tim Berners-Lee's proposal was 1989, and the web became public in the early '90s — the internet was already ~20 years old. HTTP is just one application protocol among many. Junior engineers often conflate "the internet" with "the web"; keeping them separate makes it much easier to reason about email, SSH, gRPC, and WebSockets.

**Open standards beat proprietary networks.** OSI was the committee-designed, government-blessed alternative; it lost to TCP/IP, which shipped running code first. The RFC process ("rough consensus and running code") is why the internet's specs are free to read and implement. Compare this to the walled-garden networks of the same era — CompuServe, Minitel, AOL — which had better UX for a while and lost anyway.

**Security was an afterthought, and we're still paying.** The early internet was a small set of mutually trusting research institutions. There was no authentication in the core: BGP trusts what it's told, SMTP lets anyone claim any sender, DNS wasn't signed. The 1988 Morris Worm was the first real wake-up call. Almost every security layer you use — TLS, SPF/DKIM, DNSSEC, RPKI — is a retrofit onto a protocol that assumed good faith.

**Backward compatibility is the constraint that shapes everything.** IPv6 was standardized in 1998 and adoption is still partial nearly three decades later, because you can't force an upgrade on a network no one owns. NAT was the pragmatic hack that bought time and broke the end-to-end model in the process. This is the deepest lesson for a working engineer: at internet scale, deployability beats elegance, and "we'll migrate everyone later" never happens.

If you want one book, Katie Hafner's *Where Wizards Stay Up Late* covers the ARPANET era well; for the architectural reasoning, the original end-to-end paper (Saltzer, Reed, Clark, 1984) is short and still worth reading.
