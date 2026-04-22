# Network_Automation-Learning-Path

Day 1 of building real-world automation systems with n8n ⚡

Today I built a Network Device Uptime Monitor — something every IT team actually needs.

🔧 What it does:
- Runs every 5 minutes
- Checks if devices are reachable (routers, endpoints, etc.)
- Detects downtime automatically
- Sends instant alerts via Gmail
- Logs every event into Google Sheets

💡 The challenge:
n8n (Hostinger) doesn’t support direct ping commands.

So I engineered a workaround:
- Used HTTP-based reachability checks
- Built conditional logic to detect failures
- Structured it for easy scaling (multiple devices)


I also built a full IP Address Management (IPAM) system in Airtable — and I want to show you why this matters.

Most ISP and enterprise networks I've seen manage IP allocations in one of three ways:
- A shared Excel file that's always outdated
- Someone's head
- A combination of both

The result? Duplicate IPs, overlapping subnets, and 30-minute troubleshooting sessions that should have taken 2.

Here's what I built today:

- Two linked tables — Subnets and IP Assignments
- Linked records connecting every device to its subnet
- Smart views: Available IPs, Grouped by Subnet, Decommissioned
- Interface dashboard showing real-time IP utilization per subnet
- Automation: when an IP is decommissioned → NOC team gets alerted instantly

