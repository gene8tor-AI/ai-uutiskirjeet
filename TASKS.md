# TASKS — AI-uutiskirjeet GitHub Pages

## TASK-001 — Julkaise AI Morning Brief 2026-10-05
- Status: IN PROGRESS
- Implements: SPEC-3.1, SPEC-7.1, SPEC-9.1, SPEC-10.1
- Dependencies: lähdekeruu, `build_index.py`, GitHub Pages -deploy
- Affected files/components: `paivan_ai_uutiset_2026-10-05.html`, `index.html`, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`
- External resource preflight: owner Anna Korpi / gene8tor-AI; billing account ei käytössä; production environment GitHub Pages; data boundary vain julkinen HTML ja julkiset lähde-URL:t; rollback = revert julkaisucommit tai poista uusi linkki seuraavassa commitissa; no access, naming, billing or Pages-config changes; cron payload authorizes this bounded publication.
- Acceptance criteria: päivän HTML sisältää pyydetyt osiot, indeksi rakentuu, `git diff --check` läpäisee, pushataan vain rajatut tiedostot ja julkinen URL palauttaa HTTP 200.
- Test expectations: HTML-osioiden, lähde-URL:ien, git-diffin ja HTTP-vastauksen tarkistus.
- Implementation evidence: pending.
- Verification: NOT TESTED
- Gaps / follow-up: X-haun SSL-varmennevirhe; YouTube-kanavahaku SSL-varmennevirhe.
