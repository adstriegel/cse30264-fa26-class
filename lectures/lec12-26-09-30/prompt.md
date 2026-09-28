# Discussion Prompt - 09-30-26 -  Wireshark Packet Limitations

## Prompt

Why does a packet capture conducted on Wireshark on a Wi-Fi adapter for a network managed by 802.1x only capture a subset of the packets versus all packets, even when in promiscuous mode?

## Response - Claude Opus 5.5

The short answer is that "promiscuous mode" on a Wi-Fi adapter doesn't do what it does on Ethernet, and 802.1X makes it worse: even a proper over-the-air capture can't decrypt anyone else's traffic. Several layers are involved.

**1. Promiscuous mode isn't monitor mode.** When the adapter is associated as a station (managed mode), filtering happens in the NIC firmware/MAC based on the 802.11 receiver address before the OS sees anything. Most drivers ignore or only partly honor the promiscuous flag. You get:
- unicast frames addressed to your MAC
- broadcast/multicast frames from the AP
- your own transmitted frames

Frames the AP sends to other stations carry their MAC as the RA and are dropped in hardware. The driver also strips the 802.11 header and hands the stack a synthesized 802.3 frame, so you don't see control or management frames either. To see everything on the air you need **monitor (RFMON) mode**, which isn't the same thing and is poorly supported on Windows/Npcap and on many chipsets.

**2. 802.1X gives you per-station keys you don't have.** This is the key difference from a PSK network. With WPA2/WPA3-Enterprise, each station runs an EAP exchange (EAP-TLS, PEAP, etc.) with the RADIUS server. That produces a session-unique MSK, and from it a PMK that only that station and the AP know. The 4-way handshake then derives a per-station PTK from that PMK.

- In monitor mode you capture other stations' unicast data frames, but the payloads are CCMP/GCMP ciphertext. Wireshark can't decrypt them.
- On a WPA2-PSK network, by contrast, the PMK comes from the shared passphrase. Wireshark can decrypt any station's traffic if you catch its EAPOL handshake and supply the PSK. With 802.1X there's no shared secret to supply. You'd need each session's PMK/MSK, e.g., exported from the RADIUS server or the client.
- Broadcast/multicast traffic is encrypted with the GTK, which your station does hold. So you see ARP, mDNS, DHCP broadcasts, etc. in the clear but not others' unicast. That produces exactly the "subset" pattern you're seeing.
- If 802.11w/PMF is on, robust management frames (deauth, disassoc, action frames) are protected too.

**3. PHY limitations even in monitor mode.** A monitor-mode capture only decodes what the radio can demodulate:
- **One channel at a time.** Clients band-steered to other channels, bands, or APs are invisible.
- **Capability mismatch.** If your adapter supports fewer spatial streams, narrower channel width (e.g., 80 vs 160/320 MHz), or lacks HE/EHT features, it will miss frames that use them.
- **Beamforming, MU-MIMO, and OFDMA.** In 11ax/be, transmissions are steered toward specific clients, and DL-OFDMA puts a station's data in a specific resource unit. A third-party sniffer often gets poor SNR or can't reconstruct those PPDUs.
- **Ordinary loss.** Hidden terminals, clients far from the sniffer, and high MCS rates that only decode near the intended receiver all cause missed frames. The sniffer never ACKs, so nothing is retried on its behalf.

**4. Traffic that never touches the air near you.** Wired-side traffic behind the AP or controller, traffic on other APs' BSSes, and anything tunneled via CAPWAP to a controller are all outside what an over-the-air capture can see.

**Practical options:**
- For your own station's traffic, a normal managed-mode capture is fine; it's already decrypted.
- For other clients' traffic on an 802.1X network, capture on the wired side: a switch SPAN port, a controller or AP packet-capture feature, or an AP in sniffer mode that exports to Wireshark.
- Alternatively, use monitor mode with a capable adapter on the right channel and width, and decrypt only for sessions whose PMK you can extract. Wireshark accepts `wpa-psk`/PMK entries under IEEE 802.11 decryption keys, and you still need the EAPOL 4-way handshake in the capture.
