# Week 1: Remote Virtual Lab Setup & Linux Foundations

## Objective
Set up a headless virtualization environment, deploy two Linux VMs, configure network connectivity across the home network, and control the lab remotely from a primary laptop.

---
## Setup Diagram
![Lab Setup Diagram](./docs/images/lab-setup-summer26.png)

## Environment

| Component | Detail |
|---|---|
| **Lab Server** | Spare laptop (Linux Mint) |
| **Hypervisor** | VirtualBox |
| **Attacker VM** | Kali Linux |
| **Target VM** | Ubuntu Server (headless) |
| **Network Mode** | Bridged Adapter (VMs connected directly to home router) |
| **Access Method** | SSH (primary laptop → Kali VM → Ubuntu Server VM) |

---

## Key Steps

1. **Hypervisor Setup** — Installed VirtualBox on the spare laptop:
   ```bash
   sudo apt update && sudo apt install virtualbox -y
   ```

2. **Networking** — Configured both VMs with **Bridged Adapter** networking (instead of Host-Only) to place them directly on the home network, enabling remote access from the primary laptop. IPs identified via `ip a`.

3. **Remote Access** — Enabled SSH on the Kali VM:
   ```bash
   sudo systemctl enable --now ssh
   ```
   Connected from the primary laptop:
   ```bash
   ssh username@<Kali_VM_IP>
   ```

4. **SSH Key-Based Authentication** — Generated an SSH key pair on the Kali VM and deployed it to the Ubuntu Server VM for passwordless authentication:
   ```bash
   ssh-keygen -t rsa
   ssh-copy-id username@<Ubuntu_Server_IP>
   ```

---

## Milestone
✅ From the primary laptop, SSH into the Kali VM, then SSH into the Ubuntu Server VM using key-based authentication — no password prompt.
