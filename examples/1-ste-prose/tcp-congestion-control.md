TCP congestion control keeps each sender below the rate that the network path can carry. The sender holds a congestion window (cwnd), which is the maximum quantity of data that it can have in flight without an ACK.

- **Slow start:** cwnd starts at 10 packets on Linux and doubles every round trip. Slow start stops at a threshold (ssthresh) or at the first loss.
- **Packet loss:** TCP uses a loss as the sign of congestion. If 3 duplicate ACKs arrive, the sender sends the lost packet again at once and decreases cwnd by half (by 30% with CUBIC). A timeout is a stronger signal: cwnd decreases to 1 packet and slow start starts again.
- **CUBIC:** CUBIC calculates cwnd from the time since the last loss. So on fast, long-distance paths, it returns to full speed after a loss much sooner than classic TCP (Reno). Flows with different round-trip times also share a path more equally. Linux made CUBIC the default in kernel 2.6.19 (November 2006).

### The basic idea

Routers hold packets in queues of limited size. If senders put more data into a path than the path can carry, the queues fill and the routers drop packets. TCP cannot see the routers. It sees only the ACKs from the receiver, so it must find the safe rate from those ACKs.

Terms in this answer:

- **Packet:** one full-size TCP segment (1 MSS, approximately 1,460 bytes of data on Ethernet).
- **RTT (round-trip time):** the time from when the sender sends a packet until its ACK arrives. The sender sends approximately cwnd packets in each RTT.
- **ssthresh (slow-start threshold):** the cwnd value at which slow start stops.

### Slow start

At the start, the sender does not know the capacity of the path. Linux starts with cwnd = 10 packets (RFC 6928). Each packet that the receiver acknowledges adds 1 packet to cwnd. In one RTT, the receiver acknowledges a full window, so cwnd doubles each RTT: 10, 20, 40, 80, and so on.

Slow start is slow only in comparison with TCP before 1988, which sent a full receive window at once.

Slow start stops when one of these events occurs:

- cwnd reaches ssthresh. The sender then goes to congestion avoidance.
- A packet is lost. On a new connection, ssthresh starts very high, so only a loss or HyStart can end the first slow start.
- In Linux CUBIC, HyStart can end slow start before a loss. It does this when the RTT increases, because a higher RTT shows that queues start to fill.

**Congestion avoidance.** Above ssthresh, classic TCP (Reno) adds only 1 packet per RTT. After a loss, it decreases cwnd by half. This is AIMD (additive increase, multiplicative decrease). A graph of cwnd looks like a sawtooth: a slow linear increase, a sharp drop, then the same again. CUBIC replaces this linear increase.

### When a packet is lost

TCP uses a lost packet as its main sign of congestion. It finds a loss through duplicate ACKs or through a timeout. Each shows a different level of congestion.

**3 duplicate ACKs: fast retransmit and fast recovery.** Each ACK tells the sender the next packet that the receiver expects. If packet 5 is lost and packets 6, 7 and 8 arrive, the receiver sends 3 more ACKs that all say "next: 5". These are duplicate ACKs. They show that packet 5 is probably lost. They also show that later packets still arrive, so the congestion is probably light.

The sender then does these steps:

1. It sends packet 5 again at once, before the timer expires. This is fast retransmit.
2. It sets ssthresh to half of the data in flight, and sets cwnd to approximately the same value. CUBIC uses a factor of 0.7, so its decrease is 30%.
3. It continues in congestion avoidance from the new cwnd. It does not return to slow start. This is fast recovery.

Linux also uses selective ACKs (SACK) and RACK, a method based on time, to find a loss sooner than 3 duplicate ACKs. The decrease of cwnd is the same.

**Retransmission timeout (RTO).** If the ACK for a packet does not arrive before the retransmission timer expires, the sender treats this as heavy congestion. The path is probably blocked, or many packets are lost. The reaction is much stronger:

1. ssthresh decreases as above, to half of the data in flight (70% with CUBIC).
2. cwnd goes to 1 packet.
3. The sender sends the lost packet again and doubles the timeout for the next try. This is exponential backoff.
4. Slow start starts again. cwnd doubles each RTT up to the new ssthresh, and then congestion avoidance continues.

The reactions are different for a reason. Duplicate ACKs prove that data still moves, so a moderate decrease is sufficient. After a timeout, the sender has no information about the path, so it starts again from 1 packet.

### Why CUBIC is the default on Linux

**The problem with Reno.** Reno adds 1 packet per RTT, and that is much too slow on a fast, long path. Example: a 10 Gbit/s path with a 100 ms RTT and 1,500-byte packets needs a cwnd of approximately 83,333 packets. After one loss, Reno decreases cwnd to approximately 41,667. It then needs 41,667 RTTs, approximately 70 minutes, to return to full speed.

Reno is also unfair to flows with a long RTT. A flow with a 10 ms RTT adds packets 10 times as frequently as a flow with a 100 ms RTT. On a shared bottleneck, the flow with the short RTT takes a much larger share.

**What CUBIC does.** CUBIC records W_max, the cwnd just before the last loss. At the loss, it decreases cwnd to 0.7 × W_max. Then it calculates cwnd from t, the time in seconds since the loss:

`W(t) = C * (t - K)^3 + W_max`, with `C = 0.4` and `K = cbrt(W_max * 0.3 / C)`

K is the time that CUBIC needs to return to W_max. The shape of the curve:

1. Just after the loss, cwnd is far below W_max, so it grows fast.
2. Near W_max, the curve is almost flat. CUBIC stays for a long time just below the rate that caused the last loss. The path stays full, and few new losses occur.
3. After K seconds with no loss, the curve becomes steep again. The path may have more capacity now, so CUBIC goes above the old limit, first slowly and then faster.

**Why this made CUBIC the default:**

- **Fast, long paths.** In the example above, K is approximately 40 s. Reno needs approximately 70 minutes for the same recovery. The smaller decrease (30% instead of 50%) also loses less speed at each loss.
- **Fairer between RTTs.** Window growth depends on time, so a 10 ms flow and a 100 ms flow grow their windows at almost the same speed. Their shares are still unequal, but much closer than with Reno.
- **Safe on small paths.** If Reno would grow faster (short RTT, low speed), CUBIC uses the Reno rate. RFC 9438 calls this the "Reno-friendly region". So CUBIC gets at least the throughput of Reno, and it acts like Reno where Reno works well.
- **Simpler than BIC.** Linux used BIC from kernel 2.6.8 (2004). CUBIC replaced the complex window rules of BIC with one function. It also improved fairness to Reno and between RTTs.
- **A standard now.** The IETF published CUBIC as RFC 8312 (2018) and then as the Standards Track RFC 9438 (August 2023). Windows and Apple systems also use CUBIC by default.

In the current kernel source (October 2026), CUBIC is still the default. BBR from Google is available as a module, but you must select it. To see the algorithm on your machine, run this command:

```
sysctl net.ipv4.tcp_congestion_control
```
