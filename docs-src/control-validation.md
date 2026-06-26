# Control Validation

SecRouter produces the **technical evidence** an assessor needs for a CMMC Level 2/3 review of the AI gateway. This page lists each artifact, what it proves, the NIST SP 800-171 R2 control it supports, and the exact command to retrieve it.

```{admonition} Scope
:class: note
This is a **control mapping and evidence guide**, not a certification. SecRouter implements and evidences the technical controls below; the accreditation of your environment as a whole (and the shared-responsibility items at the end) is an organizational activity.
```

Every endpoint here is **admin-gated** — call it with an admin's OIDC access token:

```bash
BASE=https://secrouter.example.url
ADMIN_TOKEN=<an admin OIDC access token>
auth=(-H "Authorization: Bearer $ADMIN_TOKEN")
```

## The fast path: one-click evidence bundle

A single endpoint packages **all** of the artifacts below — health, FIPS posture, the sanitized config baseline, the audit-chain verification, recent audit, 30-day usage, runtime stats, and a live control self-assessment — into one timestamped JSON file. The admin console's **Monitor → Compliance evidence** card has a **Download evidence bundle** button for the same thing.

```bash
curl -fsS "${auth[@]}" "$BASE/admin/api/evidence" -o "secrouter-evidence-$(date +%F).json"
```

The bundle's `controls` section is a live, family-level self-assessment generated from the running configuration — a useful index for your assessor:

```json
"controls": {
  "AU-3.3.8 (audit tamper-evidence)": { "verified": true, "eventsChecked": 1284, "status": "intact" },
  "AC-3.1.3 / SC-3.13.6 (CUI flow / deny-by-default egress)": { "allowlistRules": 2, "status": "enforced" },
  "IA-3.5.3 (multifactor)": { "required": true, "status": "required" },
  "SC-3.13.11 (FIPS crypto)": { "required": true, "active": true, "status": "FIPS active" }
}
```

## Artifacts at a glance

| Artifact | What it proves | Control(s) | How to get it |
|---|---|---|---|
| Audit log | Every auth / authz / routing / usage / admin event, traceable to a principal, **metadata-only** | AU 3.3.1, 3.3.2 | `GET /admin/api/audit` · SQLite · syslog |
| Audit-chain verification | The log is **tamper-evident** (SHA-256 hash chain) | AU 3.3.8 | `GET /admin/api/audit/verify` |
| Access policy | Who may use which tier/model — least privilege | AC 3.1.1, 3.1.2, 3.1.5 | `GET /admin/api/config` → `policy` |
| Identity &amp; MFA | OIDC SSO with MFA enforced | IA 3.5.1–3.5.3 | config `oidc` · audit `auth.success` |
| Egress allow-list | CUI reaches only authorized destinations (deny-by-default) | AC 3.1.3, SC 3.13.6 | `GET /admin/api/config` → `egress` |
| Usage &amp; cost | Per-user / per-model accountability | AU 3.3.2 | `GET /admin/usage` |
| Config baseline + change log | The enforced baseline and every audited change | CM 3.4.1, 3.4.2 | `GET /config` · audit `admin.action` |
| FIPS / TLS posture | The crypto boundary | SC 3.13.8, 3.13.11 | `GET /health` · evidence `fips` |
| **Evidence bundle** | **All of the above, one JSON** | rollup | `GET /admin/api/evidence` |

## Audit trail — AU 3.3.x

Every authentication, authorization, routing, usage, and admin event is written to a hash-chained log. Records are **metadata only** — token counts, model ids, decisions, hashes — and **never** prompt or response content (CUI-safe). Event types include `auth.success` / `auth.failure`, `authz.deny` / `authz.downgrade`, `egress.deny`, `usage`, `quota.exceeded`, `admin.action`, and `anomaly`.

```bash
# Recent events, or filter by type (e.g. every authentication failure)
curl -fsS "${auth[@]}" "$BASE/admin/api/audit?limit=500"
curl -fsS "${auth[@]}" "$BASE/admin/api/audit?type=auth.failure&limit=200"
```

**Verify tamper-evidence (AU 3.3.8).** Each row chains to the prior row's SHA-256 hash; the verifier walks the whole chain and reports the first break, if any:

```bash
curl -fsS "${auth[@]}" "$BASE/admin/api/audit/verify"
# { "ok": true, "checked": 1284, "ts": "2026-06-26T12:00:00.000Z" }
```

**Forward to your SIEM (AU 3.3.x, 800-172).** Set `security.audit.sink: "both"` with a `syslog` target (RFC 5424, CEF or JSON) — see [Configuration](configuration.md). The authoritative record is the SQLite store at `security.storePath`; syslog is the SOC copy.

## Access policy &amp; identity — AC 3.1.x / IA 3.5.x

`GET /admin/api/config` returns the effective access model: the data-classification ladder, the per-group/user **policy** (allowed tiers/models, budgets, `maxClassification`, admin), the tier→model routing, and any live overrides (with provenance).

```bash
curl -fsS "${auth[@]}" "$BASE/admin/api/config"      # policy, tiers, egress, classification, overrides
```

Identity and MFA are evidenced by the `oidc` block (issuer, audience, JWKS, `requireMfa`) plus the audit trail, where each `auth.success` records `detail.mfa` for the principal.

## Egress / data-flow control — AC 3.1.3 / SC 3.13.6

The deny-by-default egress allow-list is the CUI flow control: each rule names a `provider`, the exact `allowedHost`, and the `authorizedClassifications` it may receive. Anything not listed is refused, and refusals are logged as `egress.deny`.

```bash
curl -fsS "${auth[@]}" "$BASE/admin/api/config" | python3 -c 'import json,sys;print(json.dumps(json.load(sys.stdin)["egress"],indent=2))'
curl -fsS "${auth[@]}" "$BASE/admin/api/audit?type=egress.deny"   # attempts that were blocked
```

## Usage &amp; accountability — AU 3.3.2

Per-user, per-model, per-day token and cost accounting demonstrates individual accountability and supports cost containment.

```bash
curl -fsS "${auth[@]}" "$BASE/admin/usage?groupBy=principal&days=90"   # who used what
curl -fsS "${auth[@]}" "$BASE/admin/usage?groupBy=model&days=30"
curl -fsS "${auth[@]}" "$BASE/admin/usage?groupBy=day&principal=alice@example.url"
```

## Configuration baseline &amp; change control — CM 3.4.x

The config **file** is the change-controlled baseline; the server validates it at startup and **fails closed** on anything unsafe. Every change made through the console is written back to that file (atomically, with a `.bak` backup) and recorded in the audit log as an `admin.action`.

```bash
curl -fsS "${auth[@]}" "$BASE/config"                                  # the sanitized baseline (secrets redacted)
curl -fsS "${auth[@]}" "$BASE/admin/api/audit?type=admin.action"       # config writes, reloads, restarts, policy edits
```

## Crypto / FIPS posture — SC 3.13.8 / 3.13.11

When `requireFips` is set, the server asserts FIPS-mode crypto at startup and **refuses to start** otherwise. The TLS policy (front-end termination or native) follows SP 800-52r2.

```bash
curl -fsS "$BASE/health"        # { "status":"ok", "security":"enabled", ... }  (unauthenticated liveness)
# FIPS required vs. active and the TLS config are captured in the evidence bundle's "fips" and "config.security.tls".
```

## Collect an assessment package

The one-shot bundle is usually enough, but you can also archive the individual artifacts:

```bash
BASE=https://secrouter.example.url
ADMIN_TOKEN=<admin token>
out="secrouter-evidence-$(date +%F)"; mkdir -p "$out"
get(){ curl -fsS -H "Authorization: Bearer $ADMIN_TOKEN" "$BASE$1" -o "$out/$2"; }

get "/admin/api/evidence"                         bundle.json
get "/admin/api/audit/verify"                     audit-verify.json
get "/admin/api/audit?limit=1000"                 audit-recent.json
get "/admin/api/config"                           access-config.json
get "/admin/usage?groupBy=principal&days=90"      usage-90d.json
get "/config"                                     config-baseline.json
get "/stats"                                      runtime-stats.json
tar czf "$out.tgz" "$out" && echo "wrote $out.tgz"
```

## Shared responsibility

SecRouter enforces the **application** layer. Your environment provides the rest, and your assessor will look for each:

- A **FIPS-validated** crypto module (or a FIPS-terminating front end).
- Your enterprise **IdP** and MFA.
- The **network enclave** (GovCloud / air-gap) and its boundary protections.
- **Time synchronization** (NTP) for the audit clock.
- The **SIEM** that receives the audit stream, and audit **retention** for your required window.
- **Vulnerability management** and media protection for the host.

## Control map

SecRouter's controls map to NIST SP 800-171 R2 (the technical baseline behind CMMC L2) and selected SP 800-172 enhancements. The full per-control matrix with code citations ships with the product (`docs/compliance/cmmc-control-matrix.md`); the family-level summary:

| Family | Controls | How SecRouter evidences them |
|---|---|---|
| **AC** — Access Control | 3.1.1, 3.1.2, 3.1.3, 3.1.5, 3.1.12/13 | Deny-by-default OIDC auth; per-group/user policy; egress CUI-flow control; admin-gated endpoints |
| **AU** — Audit &amp; Accountability | 3.3.1, 3.3.2, 3.3.4, 3.3.5, 3.3.8, 3.3.9 | Hash-chained metadata-only log; per-principal traceability; fail-closed writes; chain verification; admin-only access |
| **IA** — Identification &amp; Auth | 3.5.1, 3.5.2, 3.5.3 | OIDC SSO; MFA assertion (`amr`/`acr`); signed-token validation |
| **SC** — System &amp; Comms Protection | 3.13.1, 3.13.6, 3.13.8, 3.13.11 | Boundary protection; deny-by-default egress; TLS in transit; fail-closed FIPS |
| **CM** — Configuration Management | 3.4.1, 3.4.2, 3.4.6 | Validated baseline; least functionality; audited, backed-up changes |
| **SI** — System &amp; Information Integrity | 3.14.1, 3.14.6 | Minimal vetted dependencies; input validation; anomaly + rate-limit monitoring |
