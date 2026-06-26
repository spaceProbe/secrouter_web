# Install

SecRouter is a Node.js service with a near-zero dependency footprint. Pick the path that matches where you are: local dev, a secured test stack, or production.

## Prerequisites

- **Node.js ≥ 24** (it uses the built-in `node:sqlite`).
- For containers: **Docker** + Docker Compose.
- For production: an enterprise **OIDC IdP** (Keycloak, Okta, Entra, Ping) and a model endpoint you're authorized to use (e.g. Claude on **AWS Bedrock GovCloud**, or a self-hosted model).

## Local dev (security off)

The fastest way to try the router. Security is disabled by default — **dev only, not for CUI**.

```bash
git clone https://github.com/spaceProbe/secrouter.git
cd secrouter
npm install
npm run build        # → dist/server.js
npm start            # http://localhost:18800
```

Send an OpenAI-compatible request:

```bash
curl http://localhost:18800/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Hello!"}]}'
```

## Secured test stack (Docker)

A one-command stack — the **secured** router plus a mock IdP and mock model — so you can exercise SSO, policy, quotas, egress control, and the admin console without a real IdP or cloud account.

```bash
cd secrouter/deploy
docker compose -f docker-compose.test.yml up --build
./smoke-test.sh                       # 401 → 200, chat, usage, admin-gating
open http://localhost:18800/admin     # sign in (pick a test persona)
```

:::{admonition} Get a token by hand
:class: note
The mock IdP issues real signed JWTs. Grab one and call the API:
```bash
TOKEN=$(./get-token.sh admin)         # or: power | basic
curl -H "Authorization: Bearer $TOKEN" http://localhost:18800/v1/usage
```
:::

## Production

Start from the hardened reference config and the hardening guide in the repo:

- `freerouter.config.hardened.example.json` — full config (OIDC, per-user policy/quotas, egress allow-list, FIPS, audit).
- `docs/compliance/deployment-hardening.md` — the deployment runbook.

A typical production rollout:

1. Copy the hardened config to `/etc/secrouter/config.json` and fill in your IdP, egress allow-list, and policy.
2. Run the container (or the systemd unit in `deploy/secrouter.service`), mounting the config and a writable volume for the audit/usage store.
3. Terminate TLS at a FIPS-validated front end (recommended) and set `requireFips: true`.
4. Point `audit.sink` at your SIEM.

The server **fails closed** — it refuses to start if the security config is invalid or FIPS is required but unavailable.

```{admonition} Build artifact
:class: tip
`npm run build` emits `dist/server.js`; run it with `node dist/server.js`. The container image (`Dockerfile`) is multi-stage, non-root, with a `/health` healthcheck.
```
