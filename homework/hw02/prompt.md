# Prompt - Wireshark

## Prompt

What are the most important things to know about Wireshark?

## Response

Wireshark is a free, open-source network protocol analyzer, and the essentials break down into a few areas: what it does, how to capture traffic, how to filter it, and how to stay out of trouble with it.

At its core, Wireshark captures packets flowing across a network interface and lets you inspect them in detail — down to individual protocol fields, byte by byte if needed. It sits on top of libpcap/WinPcap/Npcap for the actual capture and can read live traffic or open saved capture files (.pcap/.pcapng). It understands hundreds of protocols out of the box (TCP, UDP, HTTP, DNS, TLS, and many more) and will decode and label fields automatically, which is what makes it useful for debugging rather than just staring at raw hex.

A few practical things matter most when actually using it. Capturing traffic usually requires elevated privileges (root/administrator, or a properly configured capture group on Linux) because reading raw packets off an interface is a privileged operation. On switched networks, you typically only see traffic destined to or from your own machine unless you set up port mirroring/SPAN, use a network tap, or are capturing on a hub — Wireshark can't magically see other people's traffic on a switch. Capturing on a busy interface without a filter can produce an overwhelming amount of data, so it's common to apply a capture filter (BPF syntax, applied before capture, like `host 10.0.0.5` or `port 443`) or, more often, capture everything and use a display filter afterward (Wireshark's own syntax, like `http.request` or `ip.addr == 10.0.0.5 && tcp.port == 443`) to narrow what you're looking at.

Display filters are arguably the single most important skill in Wireshark — the filter bar turns green when valid, red when not, and learning field names like `tcp.flags.syn`, `dns.qry.name`, or `http.response.code` is how you go from a wall of packets to answering a specific question. The "Follow TCP Stream" (or UDP/HTTP stream) feature is also heavily used, since it reassembles a conversation into readable form instead of packet-by-packet fragments. Encrypted traffic (TLS) shows up as opaque unless you provide decryption material — either a pre-master secret log file (via the `SSLKEYLOGFILE` environment variable, which browsers and some tools support) or, in specific setups, private keys — otherwise you'll just see the handshake and encrypted application data.

One thing worth being direct about: Wireshark is powerful enough to capture other people's traffic, including credentials sent in cleartext protocols. It's a legitimate and widely used tool for network troubleshooting, security research, and learning protocols, but running it against networks or systems you don't own or have explicit permission to monitor can be illegal (wiretapping/unauthorized access laws) depending on jurisdiction — worth keeping in mind if the use case is anything beyond your own machine or network you administer.

If you're trying to do something specific with it right now — debug an app's network calls, analyze a capture file, decrypt TLS traffic — let me know and I can get more concrete.