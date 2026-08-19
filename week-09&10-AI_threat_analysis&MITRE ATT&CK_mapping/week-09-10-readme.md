# Week 9–10: AI-Powered Threat Analysis & MITRE ATT&CK Mapping

## Objective
Integrate a generative AI model (Google Gemini) to automate security threat triage, enforcing strict, deterministic JSON output via Pydantic schema mapping — then extend that schema to classify alerts against the industry-standard MITRE ATT&CK taxonomy, mapping raw alerts to specific attacker tactics and technique IDs.

---

## Environment

| Component | Detail |
|---|---|
| **Workstation** | WSL, Python virtual environment (`~/fastapi_project`) |
| **AI Provider** | Google Gemini (`google-genai` SDK), model `gemini-3.6-flash` |
| **Framework** | MITRE ATT&CK |
| **Schema Validation** | Pydantic (`response_schema`) |
| **Secrets Management** | `.env` (`GEMINI_API_KEY`) |

---

## Key Implementation

**Part 1 — Structured AI Output**
- Defined an initial `AnalysisResult` Pydantic model (`severity`, `suggested_action`) to constrain AI output
- Queried Gemini via `client.models.generate_content()` with `response_mime_type: application/json` and `response_schema` enforcement
- Accessed results as a validated Python object (`response.parsed`) — no manual JSON parsing required

**Part 2 — MITRE ATT&CK Mapping**
- Expanded the schema into `MitreThreatAnalysis`, adding `mitre_tactic_name`, `mitre_technique_id`, and `mitre_technique_name` alongside `severity` and `suggested_action`
- Added a `system_instruction` defining the AI's role as a SOC analyst, constraining its output to valid MITRE tactic/technique mappings rather than free-form guessing
- Tested against a mock Suricata alert (protocol decode error on port 22) to validate end-to-end classification

---

## Troubleshooting Log

| Issue | Cause | Fix |
|---|---|---|
| `404 NOT_FOUND` | `gemini-2.5-flash` deprecated | Switched to `gemini-3.6-flash` |
| `403 PERMISSION_DENIED` | Google Cloud project flagged/restricted | Generated a new API key under a clean project |
| `404 NOT_FOUND` (schema) | Legacy `gemini-1.5-flash` doesn't support `response_schema` | Reverted to `gemini-3.6-flash`, which supports structured output |

---

## Milestones

✅ **Structured output** — submitted a live threat scenario (anomalous connection spike on a database server) and received a schema-validated response:
```
Severity level: Critical
Action plan   : Restrict direct external access via firewall rules, implement
                rate limiting and automated IP blocking, and enforce access
                through a VPN or bastion host.
```

✅ **MITRE mapping** — script correctly maps a raw alert to a specific MITRE technique:
```
Severity      : Medium
Tactic        : Discovery
Technique ID  : T1046
Technique Name: Network Service Discovery
Suggested Action: Investigate the source IP for broader scanning activity and
                   ensure port 22 access is restricted.
```

---

## Key Learnings

- **Structured output matters for automation.** Freeform AI text is fragile to parse; a downstream script (e.g. the Week 8 Netmiko blocker) would break on conversational filler. Schema enforcement guarantees a reliable, machine-safe contract.
- **Error triage.** Distinguished code errors, API-versioning errors (404), and account/platform-level blocks (403) as separate failure classes requiring different fixes.
- **Taxonomy grounding beats free-form classification.** Asking an AI model to "identify the attack type" invites inconsistent labels (e.g. "scanning," "recon," "probe" for the same event). Anchoring the schema to MITRE's fixed technique IDs (`T1046`, `T1110`, etc.) forces the model to commit to a standardized reference point that any human analyst — or downstream automation — can act on unambiguously.
- **`system_instruction` is a scoping tool, not just a persona.** Framing the model as a SOC analyst wasn't cosmetic — it set the boundaries of the taxonomy the model was expected to reason within, which noticeably improved mapping accuracy compared to an unscoped prompt.
- **This is the bridge from detection to context.** Week 4's parser could tell *that* something happened; this step tells *what kind* of attack phase it represents. That distinction — raw signature vs. attacker intent — is what separates simple alerting from actual threat analysis, and it's the piece that makes automated response (Week 8) decisions defensible rather than arbitrary.

**Google GenAI SDK notes:** the modern `client.models.generate_content` interface processes the schema natively, so results are accessed directly as a validated Python object via `response.parsed` — no manual `json.loads()` parsing required.
