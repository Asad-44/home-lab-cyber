# Week 4: Alert Generation & Python Parsing

## Objective
Trigger Suricata alerts via live attacks, confirm structured JSON logging (`eve.json`), and build a Python script to parse and display alerts in real time.

---

## Environment

| Component | Detail |
|---|---|
| **Workstation** | Primary laptop (WSL), two terminal sessions side-by-side |
| **Attacker Terminal** | SSH into Kali VM |
| **Target Terminal** | SSH into Ubuntu Server VM |
| **Log Source** | `/var/log/suricata/eve.json` |
| **Parser** | Python 3 (`json` module) |

---

## Key Steps

1. **Verify JSON Logging** (on Ubuntu Server):
   ```bash
   sudo tail -f /var/log/suricata/eve.json
   ```
   Confirmed live traffic on the bridged interface is being written to `eve.json`.

2. **Trigger Alerts** (from Kali):
   Ran Nmap scans and Hydra SSH brute-force attacks against the Ubuntu Server VM's bridged IP.

3. **Build the Python Parser** (on Ubuntu Server):
   ```bash
   nano alert_monitor.py
   ```
   Script logic:
   - Open and tail `/var/log/suricata/eve.json`
   - Parse each new line with the `json` module
   - Extract `timestamp`, `src_ip`, and `alert.signature`
   - Print a formatted alert line

---

## Screenshots

![w4-ss-1](./docs/images/w4-1.png)

![w4-ss-2](./docs/images/w4-2.png)

---

## Milestone
Running `alert_monitor.py` on the Ubuntu Server while a Hydra attack executes from Kali produces real-time, human-readable alerts, e.g.:
```
[2026-03-30T14:32:10] ALERT: SSH brute force attack detected from 192.168.1.15
```
