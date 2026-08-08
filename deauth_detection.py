from scapy.all import rdpcap, Dot11
from collections import defaultdict

import sys

DEAUTH_SUBTYPE = 0x0c
THRESHOLD_FPS = 10  

if len(sys.argv) != 2:
    print("Usage: python3 deauth_detection.py <pcap_file>")
    sys.exit(1)

pcap_file = sys.argv[1]
packets = rdpcap(pcap_file)

print(f"[+] Loaded {len(packets)} packets from {pcap_file}")

deauth_events = defaultdict(list)

for pkt in packets:
    if pkt.haslayer(Dot11):
        dot11 = pkt[Dot11]
        if dot11.type == 0 and dot11.subtype == DEAUTH_SUBTYPE:
            timestamp = float(pkt.time)
            src = dot11.addr2
            dst = dot11.addr1
            deauth_events[src].append(timestamp)


attack_detected = False

print("\n[+] Deauthentication Analysis Results")

for src, times in deauth_events.items():
    times.sort()
    for i in range(len(times)):
        window_start = times[i]
        window_end = window_start + 1
        count = sum(1 for t in times if window_start <= t < window_end)

        if count > THRESHOLD_FPS:
            print(f"[!] DEAUTH FLOOD DETECTED")
            print(f"    Source MAC: {src}")
            print(f"    Frames/sec: {count}")
            print(f"    Time window start: {window_start:.2f}")
            attack_detected = True
            break

if not attack_detected:
    print("No deauthentication attack detected")

