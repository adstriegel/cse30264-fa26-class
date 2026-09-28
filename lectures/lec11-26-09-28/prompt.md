# Discussion Prompt - 09-28-26 -  IP Notation

## Prompt

Explain the difference between IPv4 addresses that are listed as `129.74.*.*` versus `129.74/16` and why or how those distinctions matter to a software engineer.

Give an example of how those notations might be used.

Do those have anything to do with the control plane or the data plane?

## Response - Claude Opus 5.5

## The short version

**`129.74.*.*`** is a *wildcard pattern*: an informal, human-oriented way of saying "any address whose first two octets are 129 and 74." It is textual, and it can only work at octet boundaries.

**`129.74/16`** is *CIDR notation*, short for `129.74.0.0/16`. It means "the first 16 bits are fixed, and the remaining 16 bits vary." It describes a network prefix as a bitmask.

For this particular case, both describe the same 65,536 addresses, 129.74.0.0 through 129.74.255.255. The difference is in what each notation can express and how software interprets it.

## Why the distinction matters to a software engineer

**1. Expressiveness.** Wildcards only give you /8, /16, /24, or /32. CIDR can express any prefix length. Suppose a department owns `129.74.16.0/20` (129.74.16.0–129.74.31.255). There is no single wildcard for that range; you would need sixteen `129.74.N.*` entries. Real-world allocations, cloud VPC subnets, and ISP blocks are rarely octet-aligned, so code that only understands wildcards can't represent them.

**2. Matching semantics.** A CIDR membership test is arithmetic:

```
(addr & mask) == (network & mask)
```

Wildcard matching tends to get implemented as string matching, and that is where bugs creep in. A classic one:

```python
ip.startswith("10.1")        # intended 10.1.*.*, but also matches 10.100.2.3, 10.19.0.1 ...
re.match(r"129.74.", ip)     # unescaped dots match any character
```

Treating addresses as strings instead of 32-bit integers is a recurring source of access-control mistakes.

**3. Parsing ambiguity of the abbreviated form.** `129.74/16` drops the trailing zeros, and parsers disagree about what that means:
- iproute2 (`ip route add 10/8`) reads it the way you'd expect.
- Python's `ipaddress` module rejects it outright.
- Legacy `inet_aton()`-style parsers read the two-part string `129.74` as `129.0.0.74`, because the last component fills the remaining 24 bits.

The safe practice is to always write and store the full form, `129.74.0.0/16`.

**4. Prefix vs. pattern.** CIDR denotes a *prefix*, and prefixes have structure:
- They nest, so `129.74.16.0/20` is inside `129.74.0.0/16`.
- They aggregate.
- They support longest-prefix-match, where the most specific rule wins.

Wildcards are just sets of addresses, with no hierarchy for tooling to reason about.

**5. IPv6.** Wildcard notation effectively collapses for IPv6. CIDR carries over directly, for example `2001:db8::/32`. Code built around CIDR works for both address families.

## Examples in practice

Application-level allowlist (Python):
```python
import ipaddress
campus = ipaddress.ip_network("129.74.0.0/16")
ipaddress.ip_address("129.74.33.5") in campus   # True
```

Other common places the notations show up:
- **Host firewall:** `iptables -A INPUT -s 129.74.0.0/16 -p tcp --dport 22 -j ACCEPT`
- **Web server:** `allow 129.74.0.0/16; deny all;` (nginx)
- **Cloud and Kubernetes:** AWS security groups, Azure NSGs, and `NetworkPolicy.ipBlock` all require CIDR.
- **Databases:** PostgreSQL's `inet`/`cidr` types support containment queries like `WHERE client_ip << '129.74.0.0/16'`.
- **Where wildcards survive:** older configs such as TCP wrappers (`sshd: 129.74.`), documentation, and ad hoc log grepping.

A related variant worth knowing is the Cisco ACL "wildcard mask": `permit ip 129.74.0.0 0.0.255.255`. It is an inverted mask where 1 bits mean "don't care." Unlike CIDR, it can even be non-contiguous, which is powerful but easy to get wrong.

## Control plane or data plane?

Both are involved, in different roles.

**Control plane.** CIDR is the language of routing. BGP advertises `129.74.0.0/16` to the Internet, routers aggregate and filter on prefixes, and the RIB is built from them. The CIDR/VLSM change in 1993 was itself a control-plane change: it replaced classful routing so prefixes could be allocated and aggregated at arbitrary lengths. Firewall and ACL rules written in CIDR are likewise configured through the control or management plane.

**Data plane.** The notation itself never touches a packet. What the control plane computes gets compiled into the FIB or TCAM, and the data plane then does per-packet longest-prefix match or masked comparison at line rate. That masked comparison is exactly the `(addr & mask) == net` operation above, in hardware or in fast lookup structures like tries.

**Wildcards** belong to neither plane natively. They are a human and application-layer convenience that has to be translated into prefix/mask form before a router or firewall can enforce it.

A useful way to frame it: CIDR is how the control plane *describes* address space, and the mask-and-compare operation it implies is what the data plane *executes*.
