<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg" />
    <img src="assets/logo.svg" alt="SecRouter — Secure AI API Router" width="300" />
  </picture>
</p>

# SecRouter — marketing site

The landing page for [SecRouter](https://github.com/spaceProbe/secrouter), built to the designer handoff (`Secure AI API Router Logo` bundle). Static, dependency-free, SEO-optimized.

**Design system:** warm-sand light theme (`#ece8dc`) with dark-olive bands (`#232a16`), olive accent (`#54672f`), IBM Plex Mono (headings/labels/data) + IBM Plex Sans (body). New hexagon "routing badge" logo.

## Run locally

```bash
python3 -m http.server 8000     # http://localhost:8000
```

## Deploy

Static files — host on GitHub Pages, Netlify, Cloudflare Pages, or S3/CloudFront. No build step.

## Claims — accurate to the shipped product

The copy was reworked to match what SecRouter actually does today. The original handoff's unverifiable / unbuilt claims were removed:

- **Removed:** SOC 2 Type II · flat "FIPS 140-2" · "FedRAMP — in process" · ITAR-aware · PII redaction · prompt-injection guard · SAML/SCIM · "SecRouter, Inc." · "book a briefing with our team".
- **Now claims (all real in the codebase):** OIDC SSO + MFA · per-user/group policy & model allowlists · budgets + rate limits with hard auto-cutoff · smart routing · deny-by-default egress + data-classification gate · hash-chained, metadata-only audit · self-hosted / GovCloud / air-gap · FIPS-*aware* · NIST 800-171 R2 / CMMC L3 **control mapping** (framed as alignment, not certification).
- The hero "inspected request" panel now demonstrates the real flow (authenticate → allowlist → budget → route → log) rather than redaction.

If you later earn SOC 2 / FedRAMP or ship features like PII redaction, add those claims back when they're real.

## Also before launch

1. **Replace the domain** `https://secrouter.io` in `index.html`, `robots.txt`, `sitemap.xml`.
2. **Wire the CTAs.** "Request a briefing" / "Contact" currently use a `mailto:sales@secrouter.io` placeholder; "Read the docs" points at the GitHub repo. Point them at your real booking/contact flow.
3. **Fonts (optional).** IBM Plex loads from Google Fonts. For an air-gapped/privacy-strict deploy, self-host the woff2 files and swap the `<link>` for `@font-face`.
4. The `og-image.png` is rendered from `og-image.svg` — re-run `rsvg-convert -w 1200 -h 630 og-image.svg -o og-image.png` if you edit it.

## Structure

```
index.html     semantic page + SEO head (meta, OG, Twitter, JSON-LD), IBM Plex
security.html  security brief page
styles.css     handoff design tokens (sand + dark olive), responsive
script.js      mobile nav, sticky nav, scroll-reveal, spend count-up
og-image.svg   social card source → og-image.png
favicon.svg    hexagon routing mark on olive tile
robots.txt · sitemap.xml
docs-src/      Sphinx docs source (MyST markdown, Furo theme)
docs/          built docs site, served at /docs/  (regenerate; see below)
```

## Docs (Sphinx)

The product docs are a Sphinx site (Furo theme, MyST markdown) served under `/docs/`. The site's "Docs" links point to `docs/index.html`.

Rebuild after editing anything in `docs-src/`:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r docs-src/requirements.txt
sphinx-build -b html docs-src docs && touch docs/.nojekyll
```

`docs/` is committed so it deploys with the static site (no build step on the host). `.nojekyll` (repo root + `docs/`) keeps GitHub Pages from stripping the `_static/` folder.
