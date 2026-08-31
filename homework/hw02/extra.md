# Extra Fun - Wireshark

This part is not required but remember, the Spiderman principle applies here, great power, great responsibility. Keep it short / purely for small testing purposes.  We will intentionally gather and analyze packet captures later in the class.

Try capturing a few packets on Wireshark using your Wi-Fi adapter to see if it works.  If you are connected to `eduroam`, you will only see packets for your device courtesy of the 802.1x session key. Please limit this strictly to `eduroam` or an access point / SSID that you own or control.

You are also welcome to see if your Wi-Fi adapter supports monitor mode.  Note that monitor mode will typically disconnect you temporarily from Wi-Fi.  This allows you to see "everything' on the particular Wi-Fi channel, specifically the various control packets.  However, you will not be able to decrypt the packet payloads for `eduroam`.

You can see which adapter might be active courtesy of the adapter list in Wireshark (one that has a line that is going up and down occasionally versus others that are strictly flat lines).

No submission is required for this part, this is strictly for your own personal learning before we get to it officially for the class.