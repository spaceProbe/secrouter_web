# Usage

SecRouter speaks the **OpenAI chat-completions API**, so most clients work by changing one setting: the base URL.

## Authenticate

When security is enabled, every request (except `/health`) must carry a **bearer JWT** from your IdP:

```
Authorization: Bearer <token>
```

- **Interactive users** sign in through your IdP and the client forwards the access token.
- **Machine clients** (CLI, pipelines) use the OIDC **client-credentials** grant to obtain a token.

A request with no token, an invalid token, or one missing MFA is rejected with `401`.

## Make a request

```bash
curl https://secrouter.example.url/v1/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "auto",
        "messages": [{"role": "user", "content": "Summarize this contract clause…"}]
      }'
```

Use `"model": "auto"` to let the classifier choose, or name a specific model to pass through (subject to your allowlist).

Streaming works as usual — set `"stream": true` and read the SSE response.

## Smart routing & overrides

With `auto`, a weighted classifier scores each request and routes to the cheapest capable tier. Override it inline when you know better — the prefix is stripped before the model sees it:

```text
/simple   What's 2+2?
/max      Analyze this distributed system for race conditions
[complex] Refactor this module to use dependency injection
deep mode: Why does this recursive CTE produce duplicates?
```

| Aliases | Tier |
|---|---|
| `simple`, `basic`, `cheap` | SIMPLE |
| `medium`, `balanced` | MEDIUM |
| `complex`, `advanced` | COMPLEX |
| `max`, `reasoning`, `think`, `deep` | REASONING |

## Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `POST /v1/chat/completions` | user | Route & forward (OpenAI-compatible) |
| `GET /v1/models` | user | List configured models |
| `GET /v1/usage` | user | Your own token / cost usage |
| `GET /health` | open | Liveness probe |
| `GET /admin` | open shell | Admin web console (OIDC PKCE login) |
| `GET /admin/usage`, `/admin/api/*` | admin | Org usage + policy/model config |
| `GET /stats`, `/config`, `POST /reload-config` | admin | Operations |

## See your usage

Any user can check their own spend:

```bash
curl -H "Authorization: Bearer $TOKEN" https://secrouter.example.url/v1/usage
```

```json
{
  "principal": "alice@example.url",
  "usage": { "last24h": { "requestCount": 12, "inputTokens": 30400, "costUsd": 0.21 } },
  "budgets": [{ "window": "day", "maxCostUsd": 25 }]
}
```

When a budget or rate limit is exceeded, requests return `429` until the window rolls over.

## Admin console

Browse to **`/admin`** and sign in (OIDC PKCE). Admins can:

- **Monitor** per-user / model / day usage and cost.
- **Configure** group and per-user policies and tier→model routing — changes are written to an audited overrides layer and applied live.
- **Add model endpoints** (below) — register a local / on-prem model with a guided wizard.
- **Review** the hash-chained audit trail.

## Add a local or on-prem endpoint

The **Models** tab has a guided wizard for registering a self-hosted, OpenAI-compatible model server (vLLM, Ollama, TGI, LM Studio, or any in-boundary endpoint):

1. **Connect** — enter the base URL (e.g. `http://llm.internal:8000/v1`) and auth (an env-var name, a one-time token used only for the test, or none — many on-prem servers need no key), then **Test endpoint**. SecRouter probes it and lists the models it serves.
2. **Select & price** — pick the models to register and set their `$`/M-token rates (default `0` for self-hosted compute, so per-user budgets and cost reports still apply). Optionally make one the primary for a routing tier.
3. **Set egress** — choose the data classifications this destination may receive. This writes a deny-by-default egress rule, so the endpoint is only reachable for those classifications.
4. **Validate → Apply → Reload** — SecRouter validates the change, writes it to the **config file** (atomically, with a `.bak` backup — the file stays your change-controlled source of truth), and you apply it with a no-downtime **Reload** or a full **Restart**.

Every step is admin-only and audited. The probe is restricted to in-boundary hosts by default (set `SECROUTER_PROBE_ALLOW_HOSTS` to allow others). Because a new endpoint always comes with an explicit, validated egress rule, the deny-by-default CUI boundary is preserved.

## Client integration (OpenAI SDKs)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://secrouter.example.url/v1",
    api_key=token,   # your OIDC access token
)
resp = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "Hello"}],
)
```
