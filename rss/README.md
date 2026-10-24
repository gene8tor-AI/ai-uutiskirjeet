# Original-news RSS
Public feed: https://gene8tor-ai.github.io/ai-uutiskirjeet/feeds/ai-news.xml

Add that URL in start.me's RSS widget (Edit → RSS feed URL). No login/token is needed.
These are original upstream titles, article links, publication times and available snippets/images, not AI-generated newsletter summaries. Source-provided Google News article links may redirect through Google News. Not every source supplies an image or summary. Missing images are now supplemented from public publisher Open Graph / Twitter preview metadata (SPEC-3.6.1). Original feed images take precedence; no image is fabricated. Google News wrappers are resolved only to fetch publisher metadata; original article links and GUIDs stay unchanged. Generic Google News preview logos are never used.

`sources.json` matches the current ingestion source configuration (production secret version2), verified 2026-10-24. It is a versioned read-only mirror, not a live Notion projection. When changing Cloud Run ingestion sources, update this registry and verify parity. No Notion or cloud credential is used by this exporter.

Dashboard export retains up to 100 unique items from 7 days (up to 10 per source) to give readers history. This does not alter the Notion ingestion's 24-hour/25-item boundaries. Previous fresh items survive source outages. Total outage/zero eligible items fails closed and preserves the last published XML. `feeds/status.json` reports refresh status; an old `lastBuildDate` indicates stale delivery, not a fresh empty feed.

GitHub Actions refreshes at 03:25, 10:25,16:25 UTC, with possible GitHub scheduling delays. This is 06:25/13:25/19:25 in Finnish summer time and 05:25/12:25/18:25 in winter time. Run manually with workflow_dispatch. Source fetches and generated XML are bounded. No AI calls, email, private news, subscriptions, extra cloud infrastructure or Pages/IAM/billing settings.

Run locally from repo root:
```
python3 -m unittest discover -s rss -p 'test_*.py' -v
python3 rss/export_feed.py
python3 rss/verify_published.py
```
Publication workflow commits only the two feed snapshots, explicitly requests the existing legacy Pages build, and verifies HTTP200, XML and byte equality. It never rebuilds the newsletter index or changes existing publications. Actual start.me thumbnail/layout rendering requires an account-side visual check. Use an RSS widget’s menu → Edit feeds → paste the complete URL → Add; the general Add-widget News search can return no results for an unregistered custom URL.

On total upstream failure, the workflow publishes the failure status while retaining the previous XML and finishes red. No empty feed replaces the last good snapshot. On this Mac's system Python, local verification needs `SSL_CERT_FILE=/etc/ssl/cert.pem` (verified system CA trust); GitHub Ubuntu runners use their standard trusted CA bundle. Certificate verification is never disabled.

## Publisher preview lookup
The dependency-free `preview_images.py` helper handles at most the selected100items, with4workers and a90-second admission budget. Each request has an8-second timeout, at most5redirects and a1MiB response read cap. Only public destinations are requested: DNS resolution is deadline-limited, every connection is pinned to a validated public IP, and HTTPS still verifies the original hostname/certificate. Redirect hops use the same checks and absolute request deadline. Images must have safe public HTTPS URLs. No image binary, page body, cookies or credentials are stored; previews link to the publisher/CDN. No login, paywall or anti-bot challenge is bypassed.

Images already in the upstream feed or previous fresh snapshot are reused without metadata requests. Per-article failures keep the original item text; a failure of the entire image helper also falls back to normal news export. `feeds/status.json.images` reports source/reused/article/unavailable/budget counts. The Google public article-resolution RPC is an undocumented best-effort dependency and may change or rate-limit; failures are reported through missing-image counts, never a substituted Google logo. Missing images are retried at the next normal feed refresh. No new API key, paid service, source-list replacement or cloud change.
