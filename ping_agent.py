"""
=============================================================
  Network Uptime Ping Agent  — WAT Framework
  Runs on your laptop (LAN side), reports to Hostinger n8n
=============================================================
  HOW IT WORKS:
    1. Pings each router using ICMP (subprocess ping command)
    2. POSTs results as JSON to your n8n Webhook URL
    3. n8n handles Email alert + Google Sheets logging

  SETUP:
    1. Edit the DEVICES list and N8N_WEBHOOK_URL below
    2. Run manually first: python ping_agent.py
    3. Schedule via Windows Task Scheduler (every 5 minutes)
=============================================================
"""

import subprocess
import platform
import json
import urllib.request
import urllib.error
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIG — Edit these values
# ─────────────────────────────────────────────

N8N_WEBHOOK_URL = "https://merakiincubator68.app.n8n.cloud/webhook-test/network-ping"

DEVICES = [
    {"name": "TP-Link Router – HQ",   "ip": "192.168.1.1",  "location": "Head Office"},
    {"name": "MikroTik – Branch A",   "ip": "192.168.1.2",  "location": "Lagos Branch"},
    {"name": "MikroTik – Branch B",   "ip": "10.0.0.1",     "location": "Abuja Branch"},
]

PING_TIMEOUT_SECONDS = 3   # How long to wait per ping
PING_COUNT = 2             # Number of ping packets to send

# ─────────────────────────────────────────────
#  PING FUNCTION
# ─────────────────────────────────────────────

def ping_device(ip: str) -> dict:
    """
    Uses the OS ping command (works on Windows & Linux).
    Returns dict with: success (bool), response_time (str), error (str)
    """
    os_type = platform.system().lower()

    if os_type == "windows":
        cmd = ["ping", "-n", str(PING_COUNT), "-w", str(PING_TIMEOUT_SECONDS * 1000), ip]
    else:
        # Linux / macOS
        cmd = ["ping", "-c", str(PING_COUNT), "-W", str(PING_TIMEOUT_SECONDS), ip]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=PING_TIMEOUT_SECONDS * PING_COUNT + 2
        )

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Extract average response time from ping output
        response_time = "N/A"
        if success:
            if os_type == "windows":
                # Windows: "Average = 4ms"
                for line in output.splitlines():
                    if "Average" in line or "average" in line:
                        parts = line.strip().split("=")
                        if len(parts) >= 2:
                            response_time = parts[-1].strip()
                            break
            else:
                # Linux: "rtt min/avg/max/mdev = 1.2/2.3/3.4/0.5 ms"
                for line in output.splitlines():
                    if "avg" in line or "rtt" in line:
                        parts = line.split("/")
                        if len(parts) >= 5:
                            response_time = f"{parts[4].split()[0]}ms"
                            break

        return {
            "success": success,
            "response_time": response_time,
            "error": "" if success else "No response (ICMP timeout or host unreachable)"
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "response_time": "N/A", "error": "Ping command timed out"}
    except Exception as e:
        return {"success": False, "response_time": "N/A", "error": str(e)}


# ─────────────────────────────────────────────
#  SEND TO N8N WEBHOOK
# ─────────────────────────────────────────────

def send_to_n8n(payload: list) -> bool:
    """
    POSTs the full results array to the n8n webhook.
    Returns True if successful.
    """
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        N8N_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"  ✅ Sent to n8n — HTTP {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  ❌ n8n webhook error: HTTP {e.code} — {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"  ❌ Could not reach n8n: {e.reason}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error sending to n8n: {e}")
        return False


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    now = datetime.now()
    timestamp     = now.isoformat()
    date_str      = now.strftime("%d/%m/%Y")
    time_str      = now.strftime("%H:%M:%S")
    checked_at    = f"{date_str} {time_str}"

    print(f"\n{'='*52}")
    print(f"  Network Ping Agent — {checked_at}")
    print(f"{'='*52}")

    results = []

    for device in DEVICES:
        print(f"\n  Pinging {device['name']} ({device['ip']}) ...")
        ping_result = ping_device(device["ip"])

        status = "UP" if ping_result["success"] else "DOWN"
        icon   = "🟢" if status == "UP" else "🔴"

        print(f"  {icon} Status: {status}  |  Response: {ping_result['response_time']}")
        if ping_result["error"]:
            print(f"     Error: {ping_result['error']}")

        results.append({
            "name":          device["name"],
            "ip":            device["ip"],
            "location":      device["location"],
            "status":        status,
            "responseTime":  ping_result["response_time"],
            "errorMessage":  ping_result["error"],
            "timestamp":     timestamp,
            "dateStr":       date_str,
            "timeStr":       time_str,
            "checkedAt":     checked_at
        })

    print(f"\n  Sending {len(results)} result(s) to n8n...")
    send_to_n8n(results)
    print(f"\n{'='*52}\n")


if __name__ == "__main__":
    main()
