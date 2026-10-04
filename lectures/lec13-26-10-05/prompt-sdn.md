# SDN in the Undergraduate Networking Curriculum

Notes on how much Software Defined Networking (SDN) deserves in an undergraduate course, a glossary of related terms, a closer look at Google's B4 and Microsoft's SWAN, and how programmable hardware (Tofino, NVIDIA SmartNICs/DPUs) fits in.

---

## 1. How important is SDN for undergraduates?

Mostly less than Kurose and Ross suggest, though the core idea deserves a place.

### What's worth keeping

The conceptual move Kurose and Ross made, splitting the network layer into **data plane** and **control plane**, is one of the better pedagogical choices in the book. It:

- Gives students a clean way to see routing as a computation separate from forwarding.
- Frames "distributed vs. logically centralized control" as a real design tradeoff rather than a historical accident.
- Lets generalized **match+action** forwarding unify destination-based forwarding, firewalls, NAT, and load balancing under one abstraction.

That framing is durable, and it makes link-state and distance-vector routing easier to motivate, because students can see what problem the distributed approach is solving and what it costs.

### What's overweighted

The specific SDN machinery reflects the 2012–2016 moment when OpenFlow looked like it would reshape networking. That includes OpenFlow message types, controller architectures, and the ONOS/OpenDaylight case studies. It didn't reshape networking the way the hype suggested. The ideas won, but mostly:

- Inside hyperscalers (B4/SWAN-style WAN traffic engineering, datacenter fabrics)
- In SD-WAN products
- In programmable data planes (P4, eBPF/XDP)

Few undergrads will ever touch an OpenFlow controller. Most will meet "SDN" as cloud networking: VPCs, security groups, overlay networks, Kubernetes CNIs. The textbook barely connects those to the SDN material, even though that's where the abstraction actually shows up for them.

### The opportunity cost

In a one-semester course, time spent on controller internals usually comes out of material that matters more to a typical graduate:

- Wireless and Wi-Fi in real depth (contention, rate adaptation, why Wi-Fi is the bottleneck in most users' lives)
- Modern transport (QUIC, BBR vs. loss-based congestion control)
- CDNs and video delivery
- Practical debugging and measurement

### Recommendation

One or two lectures:

- Teach the data/control plane separation, match+action as a generalization of forwarding, and centralized vs. distributed control as a tradeoff.
- Use the hyperscaler WAN and cloud VPC examples as motivation.
- Skip OpenFlow protocol details and controller case studies, or leave them as optional reading.
- For students headed toward systems or grad school, a P4 exercise teaches more about programmable networks than the OpenFlow material does.

**Exception:** a program with a strong cloud or datacenter emphasis could justify a deeper SDN unit, framed around how cloud networks are actually built. That's a different unit than the one the book presents.

---

## 2. Glossary

### The big players and their networks

**Hyperscaler**
A company that runs computing at enormous scale across many datacenters worldwide, such as Google, Amazon (AWS), Microsoft (Azure), and Meta. They matter here because they own their entire network end to end, so they can build custom solutions instead of buying off-the-shelf routers. That's why SDN took hold there first.

**B4 / SWAN**
The private wide-area networks (WANs) that Google (B4) and Microsoft (SWAN) use to connect their datacenters to each other. Both were described in papers in 2013 and are the classic real-world SDN success stories. Instead of letting each router independently pick paths with traditional routing protocols, a central controller sees the whole network and decides how to split traffic across links. This lets them run expensive long-haul links near full utilization rather than leaving lots of headroom. (See Section 3.)

**Datacenter fabric**
The network of switches inside a single datacenter that connects all the servers. It's usually built as a "leaf-spine" (Clos) topology: every server connects to a leaf switch, and every leaf connects to every spine switch, so any two servers are only a few hops apart with many equal-cost paths between them. "Fabric" suggests a uniform mesh rather than a hierarchy of routers.

### SDN and programmable switches

**OpenFlow**
The protocol that kicked off the SDN movement around 2008. It defines how a central controller tells a switch "if a packet matches these header fields, take this action" (forward out port 3, drop, rewrite a header, etc.). It's the concrete version of the match+action idea in the textbook. It was influential but is now rarely used directly.

**P4**
A programming language for describing how a switch processes packets. OpenFlow lets you fill in rules for a fixed set of header fields the switch already understands. P4 goes further: you can define *new* header formats and processing logic, then compile that onto programmable switch hardware. If OpenFlow is configuring a machine, P4 is reprogramming it.

### Programmable networking on ordinary servers

**eBPF**
A Linux feature that lets you load small, safety-checked programs into the running kernel without modifying or rebooting it. For networking, it means you can inspect, filter, redirect, or count packets with custom code at very high speed. It's also used heavily for monitoring and security.

**XDP (eXpress Data Path)**
A specific place to attach an eBPF program: right at the network card driver, before the kernel has done any real work on the packet. Because it acts so early, it's extremely fast. It's good for things like dropping attack traffic or load balancing at line rate.

### Cloud networking

**VPC (Virtual Private Cloud)**
Your own isolated, virtual network inside a cloud provider like AWS. You choose IP ranges, subnets, routing tables, and firewall rules ("security groups") through a web console or API, and it behaves like a private network, even though it's running on shared physical hardware alongside thousands of other customers. This is SDN in practice: you never touch a switch, but software is configuring the forwarding behavior for you.

**Kubernetes**
A system for running and managing applications packaged as containers across a cluster of machines. You tell it "run 10 copies of this web server," and it decides where they go, restarts them if they crash, and scales them up or down. Containers come and go constantly, which makes networking them tricky.

**CNI (Container Network Interface)**
The standard plug-in interface Kubernetes uses to give each container group (a "pod") its own IP address and connect it to the network. Kubernetes itself doesn't do the networking; a CNI plugin such as Calico, Flannel, or Cilium does. Cilium is notable because it's built on eBPF, which ties several of these terms together.

### How they connect

All of these are versions of the same idea from the textbook: separate *deciding* how packets should be handled (control plane) from *actually moving* them (data plane), and make the deciding part software you can program.

| Technology | Where the idea is applied |
|---|---|
| B4 / SWAN | Across continents |
| Datacenter fabrics | Inside a building |
| P4 | Inside a switch chip |
| eBPF / XDP | Inside a single server |
| VPCs / CNIs | Virtual networks that exist only in software |

---

## 3. B4 and SWAN in more detail

Both systems came out of the same problem and were published at SIGCOMM 2013, which is a big part of why the textbook leans on them.

### The problem they were solving

Google and Microsoft each run a private wide-area network connecting their datacenters across continents. Those long-haul links (leased fiber, undersea cables) are extremely expensive. Traditionally, WAN operators kept average utilization around 30–40%, leaving lots of headroom for traffic spikes and link failures. Paying for a link and using a third of it is a lot of wasted money.

Traditional routing makes this hard to fix. Protocols like OSPF or IS-IS send traffic along shortest paths, so some links get congested while longer alternative paths sit nearly empty. MPLS traffic engineering helps, but each router makes decisions with limited knowledge of what everyone else is doing.

Both companies noticed something about their own traffic. A large share of inter-datacenter traffic is not urgent: replicating storage, copying search indexes, backing up data. That traffic is **elastic**. It can be slowed down, delayed, or moved to a longer path without anyone noticing. If you could fill the "gaps" on expensive links with elastic traffic, and squeeze it out whenever urgent traffic needs the room, you could run links much hotter.

Doing that requires two things traditional networks don't have:

1. A global view of demand and capacity.
2. The ability to control how fast senders transmit.

Because Google and Microsoft own the network *and* the servers at both ends, they could have both.

### B4 (Google)

**Architecture.** Google built its own switches from commodity switching chips rather than buying traditional routers, and controlled them with OpenFlow. Each datacenter site has its own controller cluster managing local switches. Above those sits a central traffic engineering (TE) server with a global view of the whole WAN.

**How traffic engineering works.**

- Traffic is grouped into "flow groups" (roughly: traffic from site A to site B in a given priority class).
- The TE server knows each group's demand and priority, and computes an allocation that splits traffic across multiple paths (tunnels) to share capacity fairly by priority.
- When capacity runs short, low-priority bulk transfers get squeezed first, and high-priority traffic is protected.
- The allocation is pushed down to switches as forwarding rules that split traffic across tunnels in specified proportions, and senders are rate-limited at the edge so they don't exceed their share.

**Safety net.** B4 kept traditional routing protocols (BGP and IS-IS) running alongside the SDN system. If the central TE server fails or makes a bad decision, the network falls back to ordinary shortest-path routing. Traffic gets less efficient, but it keeps flowing. This hybrid design was important to getting a risky new system into production.

**Result.** Google reported running many links at close to 100% utilization, and averages around 70% over long periods, far above the industry norm. A follow-up paper ("B4 and After," SIGCOMM 2018) describes how they had to restructure it hierarchically as it grew, a good reminder that the 2013 design wasn't the end of the story.

### SWAN (Microsoft)

**Architecture.** SWAN also has a central controller with a global view, but it puts more emphasis on coordinating the *senders*. Services are classified into three tiers:

- **Interactive:** latency-sensitive, highest priority
- **Elastic:** needs to finish within a deadline
- **Background:** bulk, lowest priority

Each service reports its demand to the controller through a broker, the controller computes allocations, and then enforces them both by configuring switches and by telling hosts how fast they may send.

**Key contribution: congestion-free updates.** When the controller changes from one traffic allocation to another, switches don't all update at the same instant. During the transition, some traffic may follow old rules while other traffic follows new ones, and a link can briefly receive traffic from both, causing congestion and packet loss.

SWAN's fix is to always leave a small fraction of every link unused as **scratch capacity**. With that slack reserved, the controller can provably move from any allocation to any other through a sequence of intermediate steps, where each step never overloads any link even if switches update in any order. For example, with 10% slack the transition takes at most 9 steps. The scratch capacity isn't wasted: background traffic can use it, since that traffic tolerates being displaced during updates.

**Second contribution: limited switch memory.** Commodity switches can only hold a limited number of forwarding rules, which limits how many tunnels you can install. SWAN dynamically swaps which tunnels are installed based on current demand rather than installing every possible path.

**Result.** Microsoft reported that SWAN carried substantially more traffic than its existing MPLS-based approach, and came close to the theoretical optimum.

### Comparing the two

| | B4 (Google) | SWAN (Microsoft) |
|---|---|---|
| Main emphasis | Building and deploying a production SDN WAN | Coordinating senders and updating safely |
| Hardware | Custom switches, OpenFlow | Commodity switches with limited rule space |
| Failure handling | Falls back to traditional routing | Reserves slack for safe transitions |
| Shared idea | Central controller + elastic traffic + control of both network and senders = much higher link utilization | |

### Why this worked for them but not the whole Internet

B4 and SWAN succeed because of conditions that rarely hold elsewhere:

- A single organization controls every switch and every sender.
- There are only a few dozen sites, not millions of networks.
- Traffic types and priorities are known in advance.
- Much of the traffic is elastic and can be told to slow down.

The public Internet has none of that: independent networks that don't share information, senders nobody controls, and traffic whose importance is unknown. That's why distributed routing protocols like BGP still run the Internet, while centralized SDN control thrives inside private networks. It's a concrete case of the centralized-versus-distributed tradeoff from the textbook.

---

## 4. Programmable hardware: Tofino and NVIDIA SmartNICs/DPUs

The cleanest way to frame both is that SDN's first wave made the **control plane** programmable, and these devices make the **data plane** programmable. They sit at two different points in the network.

### Tofino: a programmable switch chip

Tofino is a switch ASIC from Barefoot Networks (acquired by Intel in 2019), and it's the chip most associated with P4.

A traditional switch chip has its packet processing hardwired. It knows Ethernet, IPv4, IPv6, VLANs, maybe MPLS, and it parses and acts on exactly those headers in a fixed order. OpenFlow didn't change that: the controller could fill in match+action tables, but only for header fields the chip already understood. If you invented a new protocol, the hardware couldn't see it.

Tofino replaces the fixed pipeline with a programmable one, an architecture called **PISA** (Protocol Independent Switch Architecture):

- **Programmable parser:** you tell it what headers exist and how to extract them, including ones you made up.
- **A series of match+action stages:** each stage has table memory and simple arithmetic units, and you decide what each one matches on and does.
- **Deparser:** reassembles the packet with whatever header changes you made.

You write this behavior in P4, compile it, and load it onto the chip. Crucially, it still runs at full line rate, terabits per second, so you gain flexibility without falling back to slow software.

**SDN connection.** Tofino completes the picture OpenFlow started. The controller still installs table entries at runtime, but now the *structure* of the tables and the parsing logic are also yours to define. That enabled research like in-network telemetry (switches stamping queue depths into packets as they pass), in-network load balancing, and even simple caching or aggregation inside the switch.

**Caveat.** Intel stopped developing future Tofino generations in early 2023. The chip is still widely used in research and teaching, and P4 lives on, but Tofino is better presented as the reference example of a programmable switch than as where the industry is headed.

### NVIDIA programmable NICs: moving the SDN data plane to the server edge

NVIDIA's line comes from its acquisition of Mellanox. There are two relevant pieces:

- **ConnectX SmartNICs:** network cards that can execute match+action rules in hardware, so flow rules from a software virtual switch (like Open vSwitch) can be offloaded to the card.
- **BlueField DPUs (Data Processing Units):** a ConnectX-style NIC plus a full set of Arm CPU cores and accelerators on the card. It's essentially a small computer sitting between the server and the network, running its own operating system.

**SDN connection.** The link here is cloud networking. When you set up subnets, routing tables, and security groups in a VPC, *something* has to enforce those rules on every packet leaving every virtual machine. Traditionally that was a virtual switch running in software on the server's own CPU, which has two problems:

1. It burns CPU cores the cloud provider would rather rent to customers.
2. It runs on the same machine as the tenant's workload, which is a security concern.

A DPU moves that whole job onto the network card. The SDN controller programs the DPU; the DPU encapsulates traffic for the virtual network, enforces firewall rules, and handles encryption; and the host CPU never sees any of it. The tenant's VM just sees a plain network interface. AWS's Nitro cards are the best-known example of this idea, built in-house, and BlueField is NVIDIA's product version that other operators can buy.

### Side by side

| | Tofino | NVIDIA SmartNIC / DPU |
|---|---|---|
| Where it sits | In the network, as a switch | At the edge, inside each server |
| What it programs | The packet pipeline of the switch | Per-server forwarding, virtualization, security |
| How it's programmed | P4 | Flow-rule offload, plus software on Arm cores (NVIDIA's DOCA SDK) |
| SDN role | Programmable data plane in the fabric | Enforces virtual network policy for each host |

### The takeaway

SDN's original promise was "separate the control plane and make it software." These devices show the second half of the story: once the brain is software, people want the muscle to be flexible too, and they push programmability into the switch chip itself or out to the very edge of the network inside each server.

---

## Further reading

- S. Jain et al., "B4: Experience with a Globally-Deployed Software Defined WAN," *ACM SIGCOMM*, 2013.
- C.-Y. Hong et al., "Achieving High Utilization with Software-Driven WAN," *ACM SIGCOMM*, 2013.
- C.-Y. Hong et al., "B4 and After: Managing Hierarchy, Partitioning, and Asymmetry for Availability and Scale in Google's Software-Defined WAN," *ACM SIGCOMM*, 2018.
- N. McKeown et al., "OpenFlow: Enabling Innovation in Campus Networks," *ACM SIGCOMM CCR*, 2008.
- P. Bosshart et al., "P4: Programming Protocol-Independent Packet Processors," *ACM SIGCOMM CCR*, 2014.
