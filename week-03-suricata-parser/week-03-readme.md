# Week 3: IDS Deployment (Suricata)

## Objective
Install and configure Suricata IDS on the Ubuntu Server VM, bind it to the bridged network interface, and verify it is actively analyzing traffic.

---

## Environment

| Component | Detail |
|---|---|
| **Target Host** | Ubuntu Server VM |
| **IDS** | Suricata |
| **Interface Mode** | Bridged Adapter |
| **Config File** | `/etc/suricata/suricata.yaml` |

---

## Key Steps

1. **Install Suricata** (on Ubuntu Server VM):
   ```bash
   sudo apt update
   sudo apt install suricata -y
   ```

2. **Identify the Bridged Interface**:
   ```bash
   ip address
   ```
   Located the interface holding the VM's assigned IP (e.g., `enp0s3`).

3. **Configure `suricata.yaml`**:
   ```bash
   sudo nano /etc/suricata/suricata.yaml
   ```
   - Set `HOME_NET` to the actual home subnet, marking the primary laptop and Kali VM as internal/trusted assets:
     ```yaml
     HOME_NET: "[192.168.1.0/24]"
     ```
   - Bind Suricata to the correct bridged interface under `af-packet`:
     ```yaml
     af-packet:
       - interface: enp0s3
     ```

4. **Update Rules & Start Service**:
   ```bash
   sudo suricata-update
   sudo systemctl enable --now suricata
   ```

---

## Screenshots
![week-03-ss-1](./docs/images/w3-1.png)
![week-03-ss-2](./docs/images/w3-2.png)

---

## Milestone
Suricata installed, configured with correct `HOME_NET` and interface bindings, running as an active service and processing live traffic on the bridged network.
