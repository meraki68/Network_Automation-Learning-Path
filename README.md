# Network_Automation-Learning-Path
Day 2 of building real-world automation systems with n8n 

Here's what I built:

- A Python agent running on a local laptop that pings TP-Link and MikroTik routers every 5 minutes using native ICMP — the most reliable way to check if a device is truly reachable
- The agent reports results to a cloud-based n8n workflow (hosted on Hostinger) via webhook — bridging the gap between a private LAN and the internet without VPNs or port forwarding
- If any device goes DOWN, an automated email alert fires instantly with the device name, IP, location, and timestamp
- Every check — UP or DOWN — gets logged to Google Sheets in real time, building a full uptime history for SLA reporting
- Windows Task Scheduler runs the whole thing silently in the background, every 5 minutes, with zero manual intervention

