# Week 8: The "Active Defender" API — SSH Automation & Active Defense

## Objective
Integrate threat intelligence querying (AbuseIPDB) with automated remediation (Netmiko/iptables) into a single FastAPI service — closing the loop from detection to active response.

---

## Environment

| Component | Detail |
|---|---|
| **API Framework** | FastAPI |
| **Threat Intel** | AbuseIPDB API |
| **Remediation** | Netmiko → Ubuntu Server VM (`iptables`) |
| **Validation** | Pydantic `IPvAnyAddress` |
| **Auth Method** | Password-based SSH (see *Security Learnings*) |

---

## Architecture

```
POST /remediate { "ip": "<target>" }
        │
        ▼
1. Validate input (Pydantic IPvAnyAddress) → rejects malformed/injected input
        │
        ▼
2. Query AbuseIPDB → abuseConfidenceScore
        │
        ▼
3. If score ≥ 50% → Netmiko SSH → check for existing rule → apply iptables DROP
        │
        ▼
4. Return JSON: score, country, ISP, remediation status, firewall log
```

---

## Key Implementation Details

- **`GET /`** — health check endpoint
- **`POST /remediate`** — core workflow: validates IP, queries reputation, conditionally triggers remote firewall block
- **Duplicate prevention** — `iptables -C` check run before `-A` to avoid redundant rule entries
- **Decision threshold** — remediation triggers automatically at `abuseConfidenceScore ≥ 50%`

---

## Security Learnings

Building this integration surfaced two real security issues, caught and addressed through iteration rather than shipped blindly. Documenting them here as part of the learning record.

### 1. Fragile sudo-prompt handling & password storage
**Issue:** The original remediation function detected a `sudo` password prompt by scanning command output for the string `"password"` and reacted by sending the stored password in response:
```python
if "password" in output.lower():
    output += net_connect.send_command_timing(ubuntu_password)
return output
```
This is a lab-grade workaround, not a production pattern — string-matching a prompt is unreliable across environments, and storing an SSH/sudo password in `.env` is a real credential-exposure risk.

**Production-correct approach:** SSH key-based authentication paired with a tightly scoped `sudoers` policy — e.g. granting `NOPASSWD` only for the exact `iptables -A/-C INPUT -s * -j DROP` command patterns, not blanket access to `iptables`. This removes password prompts entirely and limits blast radius if the automation account is ever compromised.

**Decision for this lab:** Reverted to password-based Netmiko auth for the home lab, since the target is a personal isolated VM, not a production host. The key-based / restricted-sudoers design is understood and documented as the correct approach for a real deployment — trading strict security posture for setup simplicity in a single-user, non-production environment.

### 2. Command injection via unvalidated input
**Issue:** The malicious IP was interpolated directly into a shell command:
```python
block_command = f"sudo iptables -A INPUT -s {malicious_ip} -j DROP"
```
Without validation, a crafted payload in place of a normal IP could manipulate the resulting shell command (command injection).

**Fix applied:** Replaced the raw `str` field with Pydantic's `IPvAnyAddress` type on the request model:
```python
class IPPayload(BaseModel):
    ip: IPvAnyAddress
```
FastAPI now rejects any non-IP input at the validation layer (`422 Unprocessable Entity`) before it can reach command construction — verified by submitting a payload like `192.168.100.41; rm -rf /` and confirming rejection.

**Fix applied (duplicate rules):** Added an `iptables -C` existence check before `-A`, so re-submitting the same malicious IP returns `"Rule already exists. Skipping duplication."` instead of stacking redundant rules.

---

## Milestone
✅ `POST /remediate` with a known-malicious IP (e.g. a TOR exit node) returns a full threat report and — for scores ≥ 50% — automatically connects to the Ubuntu Server VM and applies an `iptables DROP` rule, confirmed via:
```bash
sudo iptables -L -n -v
```
