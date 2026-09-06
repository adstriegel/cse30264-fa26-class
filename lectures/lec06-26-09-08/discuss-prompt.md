# Discussion Prompt - 09-08-26 - Transport Layer

While we will be discussing TCP, we will do a TCP adjacent prompt related to the lectures from last week on HTTP and the Application Layer. This prompt and response gets into the nuance of the differences in various versions of HTTP and how HTTP/3 actually brings in QUIC which runs on UDP instead of TCP.

## Prompt

What is the difference between HTTP 1.1, HTTP/2 and HTTP/3?

## Response

The main differences come down to how each version handles connections and moves data over the wire.

HTTP/1.1, from 1997, is text-based and processes one request per connection at a time in the original spec — though persistent connections (keep-alive) let a browser reuse a TCP connection for multiple sequential requests, it still suffers from head-of-line blocking: if one request is slow, others queued behind it on that connection wait. Browsers work around this by opening several parallel TCP connections (usually around six) to the same host, which has its own overhead since each connection needs its own TCP handshake and, for HTTPS, TLS handshake.

HTTP/2, standardized in 2015, introduced a binary framing layer and multiplexing: multiple requests and responses can be interleaved over a single TCP connection as independent "streams," which removes the application-layer head-of-line blocking problem HTTP/1.1 had. It also added header compression (HPACK) to cut down on redundant header data, and originally included server push (letting a server proactively send resources before they're requested), though push saw little adoption and browsers have largely dropped support for it. The catch with HTTP/2 is that it's still built on TCP, so if a single packet is lost, TCP holds up delivery of all the multiplexed streams on that connection until the lost packet is retransmitted — head-of-line blocking reappears, just at the transport layer instead.

HTTP/3, finalized in 2022, addresses that by replacing TCP with QUIC, a transport protocol built on UDP. QUIC gives each stream independent loss recovery, so a lost packet only stalls the one stream it belongs to, not the whole connection. QUIC also bakes in TLS 1.3 rather than layering it on top, which lets connections start faster (often 1-RTT or even 0-RTT for resumed connections), and it supports connection migration — a client can switch networks, like from Wi-Fi to cellular, without dropping the connection, since QUIC connections are identified by a connection ID rather than the IP/port tuple TCP relies on.

In short: 1.1 is simple but serializes work and needs multiple connections to get parallelism; 2 multiplexes over one TCP connection but is still exposed to TCP-level stalls; 3 moves to QUIC/UDP to fix that stalling and adds faster, more resilient connection setup. Adoption today is broad for HTTP/2, and HTTP/3 support is now standard in most major browsers and CDNs, though servers commonly negotiate down to older versions when needed.

## Prompt - Follow Up

Can you give me an example of a request message for each one?

## Response

Here's what each looks like, roughly as you'd see it in a debugging tool. HTTP/1.1 is genuinely sent as this text; HTTP/2 and HTTP/3 are sent as compressed binary frames, so what's shown for those is the decoded/logical view (what you'd see in browser dev tools, curl -v, or Wireshark after decoding), not literal bytes on the wire.

**HTTP/1.1** — plain text, one request:

```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

```

Note the request line packs method, path, and version together, `Host` is just a regular header (needed since one connection could theoretically serve multiple hostnames), and the blank line at the end signals the end of headers.

**HTTP/2** — a binary HEADERS frame on a stream, with the request line broken into "pseudo-header" fields and everything HPACK-compressed:

```
HEADERS frame — stream 1, flags: END_HEADERS | END_STREAM
  :method       = GET
  :scheme       = https
  :authority    = www.example.com
  :path         = /index.html
  user-agent    = Mozilla/5.0
  accept        = text/html
  accept-encoding = gzip, deflate, br
```

There's no request line or blank-line terminator anymore — the frame itself carries a length and stream ID, and `:method`, `:scheme`, `:authority`, `:path` replace what used to be the first line. Since it's a GET with no body, `END_STREAM` is set on this same frame to signal the request is complete.

**HTTP/3** — same logical header set, but framed for a QUIC stream and compressed with QPACK instead of HPACK:

```
HEADERS frame — QUIC stream 0, encoded with QPACK
  :method       = GET
  :scheme       = https
  :authority    = www.example.com
  :path         = /index.html
  user-agent    = Mozilla/5.0
  accept        = text/html
  accept-encoding = gzip, deflate, br
```

The header layout is essentially identical to HTTP/2 — HTTP/3 kept HTTP/2's semantics deliberately — the real difference is underneath: this frame travels over a QUIC stream (itself running over UDP) rather than a TCP-carried HTTP/2 stream, and QPACK is designed so that header compression doesn't reintroduce the head-of-line blocking QUIC was built to avoid.

## Prompt

Isn't UDP unreliable?  How can HTTP/3 work with UDP?

## Response

Yes, UDP itself is unreliable — no guaranteed delivery, no ordering, no congestion control, packets can be dropped or arrive out of order and UDP just doesn't care. HTTP/3 doesn't use raw UDP for the reliability story; it uses UDP purely as a thin, minimal transport that the OS and network already know how to route and forward, and then builds all the reliability itself in QUIC, which sits on top of UDP as a user-space protocol.

QUIC reimplements the things TCP normally gives you — acknowledgments, retransmission of lost packets, ordering, flow control, congestion control — but does it per-stream rather than per-connection. Each QUIC packet carries a sequence number and streams are logically independent, so if a packet carrying stream 5's data is lost, QUIC detects the gap and retransmits just that data; streams 1 through 4 aren't held up waiting for it, because there's no single ordered byte pipe that everything has to pass through in order the way there is with TCP. That's the specific thing UDP makes possible here: TCP enforces strict in-order delivery of the entire connection at the kernel level, which is exactly the behavior QUIC needs to avoid to fix head-of-line blocking, so QUIC needed a transport that stays out of the way and lets it implement ordering/reliability itself, per stream. UDP is essentially just "send this packet, best effort" with no built-in opinions, which is exactly the blank slate QUIC needs.

The reason this had to happen over UDP rather than as a new transport-layer protocol alongside TCP and UDP is deployability — middleboxes, firewalls, NATs, and OS network stacks across the internet are built to recognize and handle TCP and UDP specifically, and a brand-new transport-layer protocol would get silently dropped or mishandled by huge swaths of existing network equipment. UDP was the one widely-supported "give me raw, unopinionated packets" option available, so QUIC piggybacks on it and does the real engineering in user space, where it can iterate and evolve much faster than kernel-level TCP implementations do.

One more piece: QUIC also folds in TLS 1.3 as part of the same handshake (rather than TCP handshake, then a separate TLS handshake on top), and encrypts almost all of its own header and control information — which incidentally also protects it from those same middleboxes trying to inspect and "optimize" it based on assumptions about how TCP behaves, something that caused real deployment problems for earlier attempts at improving TCP itself.

## Prompt - Final

Isn't it difficult to test with QUIC locally due to it needing TLS and self issued certificates?

## Response

Yes, and it's a real point of friction — more than it is for HTTP/1.1 or even HTTP/2. HTTP/1.1 can run entirely in plaintext for local testing, and HTTP/2 has a defined cleartext variant (h2c) that browsers won't use but plenty of tools and internal services do for exactly this reason. QUIC has no such escape hatch: TLS 1.3 is baked into the QUIC handshake itself, not layered on afterward, so there's no way to spin up a bare, unencrypted QUIC endpoint for a quick local test. Every QUIC/HTTP-3 connection, even to localhost, needs a valid TLS handshake to establish at all.

In practice this ends up being the same problem as testing any local HTTPS service, just with no fallback — you deal with it the same ways:

Generating a self-signed cert with OpenSSL and pointing both server and client at it works, but browsers throw the usual untrusted-certificate warnings, and for QUIC specifically that can be more annoying than for regular HTTPS, since some browsers don't let you click through the normal certificate-error interstitial for a forced-QUIC connection the same way. Chrome, for example, has dedicated flags for this case: `--origin-to-force-quic-on=host:port` to force it to try QUIC against your local server, combined with `--ignore-certificate-errors-spki-list=<hash-of-your-cert's-public-key>` to allowlist that specific self-signed cert without disabling verification globally, or the blunter `--ignore-certificate-errors` for throwaway local testing.

A nicer option is mkcert, which creates a local certificate authority and installs it into your system/browser trust store, so certs it issues are trusted normally with no warnings or flags needed — it works fine for QUIC since QUIC's TLS layer doesn't care how the cert was issued, only that it validates. Caddy leans on this same idea and will auto-provision and trust local dev certificates for you, and it supports HTTP/3 out of the box, so it's a common way people get a working local HTTP/3 endpoint with minimal setup.

On the tooling side, most QUIC implementations also just expect you to hand them a cert and key and don't try to make that easier — quiche and quic-go, for instance, ship example/test certificates in their repos specifically so people aren't generating their own from scratch to run the examples. And command-line clients like curl (when built with HTTP/3 support) have the standard `-k`/`--insecure` to skip verification, or `--cacert` to trust your own CA explicitly.

So the short answer is: yes, it's unavoidable friction that HTTP/1.1 testing doesn't have, but it's the same friction as local HTTPS testing generally, and the ecosystem (mkcert, Caddy, bundled test certs) has mostly absorbed it rather than leaving people to hand-roll OpenSSL certs and insecure flags every time.
