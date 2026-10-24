# Original-news RSS
Public feed: https://gene8tor-ai.github.io/ai-uutiskirjeet/feeds/ai-news.xml

Add that URL in start.me's RSS widget (Edit → RSS feed URL). No login/token is needed.
These are original upstream titles, article links, publication times and available snippets/images, not AI-generated newsletter summaries. Source-provided Google News article links may redirect through Google News. Not every source supplies an image or summary; this exporter does not fabricate or scrape them.

`sources.json` matches the current ingestion source configuration (production secret version2), verified 2026-10-24. It is a versioned read-only mirror, not a live Notion projection. When changing Cloud Run ingestion sources, update this registry and verify parity. No Notion or cloud credential is used by this exporter.

Dashboard export retains up to 100 unique items from 7 days (up to 10 per source) to give readers history. This does not alter the Notion ingestion's 24-hour/25-item boundaries. Previous fresh items survive source outages. Total outage/zero eligible items fails closed and preserves the last published XML. `feeds/status.json` reports refresh status; an old `lastBuildDate` indicates stale delivery, not a fresh empty feed.

GitHub Actions refreshes at 03:25, 10:25,16:25 UTC, with possible GitHub scheduling delays. This is 06:25/13:25/19:25 in Finnish summer time and 05:25/12:25/18:25 in winter time. Run manually with workflow_dispatch. Source fetches and generated XML are bounded. No AI calls, email, private news, subscriptions, extra cloud infrastructure or Pages/IAM/billing settings.

Run locally from repo root:
```
python3 -m unittest discover -s rss -p 'test_*.py' -v
python3 rss/export_feed.py
python3 rss/verify_published.py
```
Publication workflow commits only the two feed snapshots, explicitly requests the existing legacy Pages build, and verifies HTTP200, XML and byte equality. It never rebuilds the newsletter index or changes existing publications. Actual start.me thumbnail/layout rendering requires an account-side visual check.

On total upstream failure, the workflow publishes the failure status while retaining the previous XML and finishes red. No empty feed replaces the last good snapshot. On this Mac's system Python, local verification needs `SSL_CERT_FILE=/etc/ssl/cert.pem` (verified system CA trust); GitHub Ubuntu runners use their standard trusted CA bundle. Certificate verification is never disabled.
