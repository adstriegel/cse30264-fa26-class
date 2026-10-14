# TCP Slow Start and Congestion Avoidance: A 100 KB Transfer Walkthrough

## Assumptions

These are the standard textbook assumptions for this example:

- There is no packet loss.
- The receiver window never limits the sender.
- There are no delayed ACKs.
- The initial CWND is 1 MSS.
- The sender transmits a full window each RTT.

## Setup

- **File:** 100 KB ÷ 1 KB MSS = **100 segments**
- **ssthresh:** 16 MSS
- **Slow Start rule:** CWND grows by 1 MSS for every ACK received, so it **doubles every RTT**.
- **Congestion Avoidance rule:** CWND grows by MSS × MSS / CWND per ACK, which works out to **+1 MSS per RTT** (linear growth).
- **Switch point:** When CWND reaches ssthresh (16), the sender leaves Slow Start and enters Congestion Avoidance.

## Round-by-Round

| RTT | Phase | CWND (MSS) | Segments sent | Cumulative sent | Remaining |
|---|---|---|---|---|---|
| 1 | Slow Start | 1 | 1 | 1 | 99 |
| 2 | Slow Start | 2 | 2 | 3 | 97 |
| 3 | Slow Start | 4 | 4 | 7 | 93 |
| 4 | Slow Start | 8 | 8 | 15 | 85 |
| 5 | **Hits ssthresh → CA** | 16 | 16 | 31 | 69 |
| 6 | Congestion Avoidance | 17 | 17 | 48 | 52 |
| 7 | Congestion Avoidance | 18 | 18 | 66 | 34 |
| 8 | Congestion Avoidance | 19 | 19 | 85 | 15 |
| 9 | Congestion Avoidance | 20 | **15** (partial window) | **100** ✅ | 0 |

## CWND Growth

Each `█` is one MSS. The `|` marks ssthresh = 16.

```
RTT 1  SS  █                                   1
RTT 2  SS  ██                                  2
RTT 3  SS  ████                                4
RTT 4  SS  ████████                            8
RTT 5  SS  ████████████████|                  16  ← reaches ssthresh
RTT 6  CA  ████████████████|█                 17
RTT 7  CA  ████████████████|██                18
RTT 8  CA  ████████████████|███               19
RTT 9  CA  ████████████████|████              20  (only 15 segments needed)
```

The knee at RTT 5 is where exponential growth gives way to linear growth.

## What Happens in Each Phase

**Slow Start (RTTs 1–5).** Each ACK adds one segment to CWND, so every segment sent produces two in the next round: 1 → 2 → 4 → 8 → 16. After four doublings, CWND equals ssthresh and the sender switches modes. By the end of RTT 5, 31 of the 100 segments have been sent.

**Congestion Avoidance (RTTs 6–9).** Each ACK now adds only 1/CWND of a segment. For example, with CWND = 16, each of the 16 ACKs adds 1/16 MSS, for a total of +1 MSS per RTT. Growth becomes slow and linear: 17, 18, 19, 20.

**Completion (RTT 9).** CWND is 20, but only 15 segments remain, so the final window is only partly used. The transfer finishes in **9 RTTs**. Count one more RTT if you include the TCP handshake.

## The Impact of ssthresh

Without the threshold, Slow Start would keep doubling: 1, 2, 4, 8, 16, 32, 64. The cumulative totals would be 1, 3, 7, 15, 31, 63, 127, so all 100 segments would be sent in **7 RTTs**.

Setting ssthresh to 16 therefore adds **2 RTTs** to this transfer. This is the trade-off Congestion Avoidance makes: once the window is near a level where congestion was previously expected, it probes for bandwidth more cautiously.

## Teaching Notes

- **Boundary convention.** Some texts treat RTT 5 as the last Slow Start round (8 → 16) and start Congestion Avoidance at RTT 6. The per-round numbers are the same either way, so the result does not change.
- **Modern initial windows.** RFC 6928 allows an initial window of 10 segments, which shortens Slow Start considerably. With IW = 10, this transfer takes 6 RTTs: windows of 10, 16, 17, 18, and 19, followed by a final RTT for the last 20 segments.
- **Delayed ACKs.** With delayed ACKs (one ACK per two segments), Slow Start grows by only about 1.5× per RTT, unless the stack uses Appropriate Byte Counting (RFC 3465).

## Practice Variants

1. Redo the table with an initial window of 10 segments.
2. Suppose a loss is detected by triple duplicate ACK during RTT 7, with TCP Reno fast recovery. What are the new ssthresh and CWND, and how many RTTs does the transfer take now?
3. Suppose ssthresh = 8. How many RTTs does the transfer take?
