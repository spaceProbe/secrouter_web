# SecRouter documentation

**SecRouter** is a self-hosted, OpenAI-compatible AI gateway that sits in front of your LLMs and enforces governance and cost control on every request: SSO authentication, per-user policy and budgets, deny-by-default egress with a data-classification gate, and a hash-chained, metadata-only audit log.

It's a drop-in endpoint — point any OpenAI-compatible client at SecRouter, change the base URL, and keep your code.

```{admonition} What it does
:class: tip
**Govern** — OIDC SSO + MFA, per-user/group model allowlists, deny-by-default egress.
**Contain spend** — per-user token & cost tracking, budgets, rate limits, smart routing.
**Prove it** — tamper-evident audit, mapped to NIST 800-171 R2 / CMMC L3 controls.
```

## Get started

```{toctree}
:maxdepth: 2

install
usage
configuration
```

- **[Install](install.md)** — run it in dev, as a secured Docker stack, or in production.
- **[Usage](usage.md)** — the API, authentication, the admin console, smart routing.
- **[Configuration](configuration.md)** — providers, tiers, and the security block.

## The request pipeline

Every call flows through four gates, with usage metered and everything logged:

```text
client ──▶ AuthN ──▶ AuthZ ──▶ route ──▶ egress gate ──▶ authorized model
          (OIDC)    (policy +   (cheapest   (deny-by-default
                     quota)     capable)     + data residency)
```

If any gate says no, the request never leaves your boundary.
