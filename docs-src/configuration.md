# Configuration

SecRouter reads a single JSON config file, resolved in this order:

1. `FREEROUTER_CONFIG` environment variable
2. `./freerouter.config.json` (working directory)
3. `~/.config/freerouter/config.json`

The `security` block is **validated at startup and fails closed** — the server refuses to boot in an unsafe configuration. Start production from `freerouter.config.hardened.example.json` in the repo.

## Shape

```json
{
  "providers": {
    "bedrock": { "api": "bedrock", "region": "us-gov-west-1", "baseUrl": "https://bedrock-runtime.us-gov-west-1.amazonaws.com" },
    "local":   { "api": "openai", "baseUrl": "https://llm.internal.example.mil/v1" }
  },
  "tiers": {
    "SIMPLE":    { "primary": "local/llama-3.3-70b-instruct" },
    "MEDIUM":    { "primary": "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0" },
    "COMPLEX":   { "primary": "bedrock/anthropic.claude-opus-4-20250514-v1:0" }
  },
  "security": { "...": "see below" }
}
```

```{list-table}
:header-rows: 1

* - Block
  - Purpose
* - `providers`
  - Backends and how to reach them (`anthropic`, `openai`, or `bedrock` with a `region`).
* - `tiers`
  - Which model serves each tier (`SIMPLE` → `REASONING`), with optional `fallback`.
* - `security`
  - Auth, per-user policy, egress control, audit, and TLS/FIPS. Off unless `enabled: true`.
```

## The `security` block

```json
"security": {
  "enabled": true,
  "requireFips": true,

  "oidc": {
    "issuer": "https://idp.example.mil/realms/cui",
    "audience": "secrouter",
    "requireMfa": true,
    "groupsClaim": "groups",
    "clientId": "secrouter-admin-console"
  },

  "classification": { "default": "CUI", "levels": ["UNCLASSIFIED", "CUI"] },

  "egress": {
    "allowlist": [
      { "provider": "bedrock",
        "allowedHost": "bedrock-runtime.us-gov-west-1.amazonaws.com",
        "authorizedClassifications": ["CUI"] }
    ]
  },

  "policy": {
    "default": { "allowedTiers": ["SIMPLE", "MEDIUM"], "budgets": [{ "window": "day", "maxCostUsd": 25 }] },
    "groups": {
      "secrouter-admins": { "admin": true },
      "power-users": { "allowedTiers": ["SIMPLE", "MEDIUM", "COMPLEX", "REASONING"] }
    }
  },

  "audit": { "sink": "both", "syslog": { "host": "siem.internal", "port": 6514, "protocol": "tcp" } },
  "tls": { "mode": "frontend" }
}
```

```{list-table}
:header-rows: 1

* - Key
  - What it controls
* - `oidc`
  - Token validation: issuer, audience, JWKS, MFA assertion, the groups claim, and the admin-console client id.
* - `classification`
  - The ordered data-classification ladder used by the egress gate.
* - `egress.allowlist`
  - **Deny-by-default** list of authorized destinations and the classifications each may receive.
* - `policy`
  - Per-group and per-user grants: `allowedTiers`, `allowedModels`, `budgets`, rate limits, `admin`, and `maxClassification`.
* - `audit`
  - `sqlite` (always) plus optional `syslog`/SIEM forwarding. Fail-closed by default.
* - `tls`
  - `frontend` (terminate at a FIPS-validated proxy — recommended) or `native`.
```

```{admonition} Keep trackJti off
:class: warning
`oidc.trackJti` enforces **single-use** tokens. Standard OIDC access tokens are multi-use bearer tokens, so leaving it on rejects the second request that reuses a token. Only enable it if your IdP issues one-time tokens.
```

## Reload without restart

Edit the config, then have an admin POST to reload — the new config is re-validated (fail-closed) before it's applied:

```bash
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" https://secrouter.example.url/reload-config
```

Policy and tier→model edits made in the **admin console** apply live without a reload.
