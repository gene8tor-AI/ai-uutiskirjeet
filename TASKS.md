# TASKS — AI-uutiskirjeet GitHub Pages

## TASK-006 — Julkaise Viikon AI-uutiskuva 2026-10-07
- Status: IN PROGRESS
- Implements: SPEC-3.3, SPEC-7.1, SPEC-7.2, SPEC-7.3, SPEC-9.1, SPEC-10.1
- Dependencies: alkuperäislähteen ja päiväyksen varmennus, kuvitus, Notion-metatieto, `build_index.py`, rajattu git-commit/push, Pages-URL:n HTTP 200 -tarkistus ja Gmail API -päiväraja.
- Affected files/components: `viikon_ai_uutiskuva_2026-10-07.html`, `images/viikon-ai-uutiskuva-2026-10-07.png`, `index.html`, uutistietokanta Notionissa, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, branch `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`, Gmail API sender `/Users/samisikila/.openclaw/workspace/scripts/send_news_link_once.py`.
- External resource preflight: owner Anna Korpi / `gene8tor-AI`; billing account ei käytössä; production environment GitHub Pages; data boundary on julkinen suomenkielinen HTML, alkuperäislähde-URL ja toimituskuvitus ilman henkilöitä, logoja tai tekstiä. Notioniin tallennetaan uutisotsikko, päivämäärä, lähde ja julkinen URL. Gmail API -viesti sisältää vain julkisen URL:n, lyhyen otsikon ja suomenkielisen johdannon vastaanottajalle `Sami.sikila@teliacompany.com`. Rollback = revert julkaisucommit ja indeksimuutos; ei käyttöoikeus-, nimike-, laskutus- tai Pages-asetusmuutoksia. Cron-payload valtuuttaa tämän rajatun julkaisun, Notion-metatiedon ja vain yhden Gmail API -lähetysyrityksen julkisen HTTP 200 -varmennuksen jälkeen.
- Acceptance criteria: yksi 30.9.–7.10.2026 julkaistu, alkuperäislähteellä varmennettu AI-uutinen; HTML, kuva ja indeksi läpäisevät rakenteellisen tarkistuksen, `build_index.py`- ja `git diff --check` -tarkistukset; rajattu commit on main-haarassa; julkinen HTML-URL palauttaa HTTP 200; Notion-tietue luetaan takaisin; Gmail API -lähettäjän SENT/SKIPPED/virhetila kirjataan.
- Test expectations: alkuperäislähteen päivämäärä- ja sisältötarkistus, kuvavaatimus, HTML-lähdelinkki, index-build, diff-check, commit-sisältö, HTTP-status, Notion-paluuarvo ja lähettäjäkomennon tulos.
- Implementation evidence: OpenAI:n alkuperäisjulkaisu `Atlassian and OpenAI expand partnership to turn enterprise knowledge into action` varmennettu 6.10.2026. Image 2 -kuvitus valmistui alkuperäisen ajon päätyttyä; kuvan silmämääräinen tarkistus vahvisti, ettei siinä ole tunnistettavia henkilöitä, logoja, kuvatekstiä tai vesileimaa. HTML-jäsennys varmisti yhden kuvatiedostoviittauksen ja yhden OpenAI-lähdelinkin; `build_index.py` ja `git diff --check` PASS.
- Verification: IN PROGRESS — GitHub Pages -commit/push, julkisen URL:n HTTP 200, Notion-tietueen takaisinluku ja Gmail API -päivärajan tulos ovat vielä varmennettavana.

## TASK-005 — Julkaise AI Morning Brief B 2026-10-07
- Status: PARTIAL
- Implements: SPEC-3.1, SPEC-7.1, SPEC-7.2, SPEC-9.1, SPEC-10.1
- Dependencies: varmennettu lähdekeruu, X-hakutila, Telco AI -aluehaku, `build_index.py`, rajattu git-commit/push, Pages-URL:n HTTP 200 -tarkistus ja Gmail API -päiväraja.
- Affected files/components: `paivan_ai_uutiset_2026-10-07_b.html`, `index.html`, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, branch `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`, Gmail API sender `/Users/samisikila/.openclaw/workspace/scripts/send_news_link_once.py`.
- External resource preflight: owner Anna Korpi / `gene8tor-AI`; billing account ei käytössä; production environment GitHub Pages; data boundary vain julkinen suomenkielinen HTML, tiivistelmät ja julkiset lähde-URL:t. Gmail API -viesti sisältää vain julkisen URL:n, lyhyen otsikon ja saman suomenkielisen johdannon vastaanottajalle `Sami.sikila@teliacompany.com`. Rollback = revert julkaisucommit ja indeksimuutos; ei käyttöoikeus-, nimike-, laskutus- tai Pages-asetusmuutoksia. Cron-payload valtuuttaa tämän rajatun julkaisun ja vain yhden Gmail API -lähetysyrityksen julkisen HTTP 200 -varmennuksen jälkeen.
- Acceptance criteria: päivän B-HTML sisältää vähintään 10 varmennettua AI-/Telco-nostoa, Telco AI Europe/USA/Asia -alaosiot ja läpinäkyvän X-hakutilan; `build_index.py` ja `git diff --check` onnistuvat; commit sisältää vain B-HTML:n ja indeksin; main-haaran Pages-URL palauttaa HTTP 200 ennen Gmail API -komentoa; lähettäjän SENT/SKIPPED/virhetila kirjataan.
- Test expectations: HTML-rakenteen, lähde-URL:ien, `git diff --check`:n, commit-sisällön ja HTTP-vastauksen tarkistus.
- Implementation evidence: Gmail- ja Notion-lähteet luettu; Telco AI -aluehaku tehty, 13 uutis-/Telco-nostoa julkaistu. X-haku epäonnistui SSL-varmennevirheeseen ja sivulla on tästä läpinäkyvä tila. `python3 build_index.py`, HTML-jäsennys (26 lähdelinkkiä) ja `git diff --check` PASS; commit `619c725` pushed to `main` vain tiedostolla `paivan_ai_uutiset_2026-10-07_b.html`. Julkinen URL palautti HTTP 200 kolmannen uusintatarkistuksen jälkeen.
- Verification: PARTIAL — GitHub Pages -julkaisu PASS: `https://gene8tor-ai.github.io/ai-uutiskirjeet/paivan_ai_uutiset_2026-10-07_b.html` palautti HTTP 200. Gmail API -komento palautti virheen `URL ei ole hyväksytty uutiskirjelinkki.`; ohjeen mukaisesti muita lähetysreittejä tai uusia yrityksiä ei tehty samana päivänä.

## TASK-004 — Julkaise AI Morning Brief 2026-10-07
- Status: DONE
- Implements: SPEC-3.1, SPEC-7.1, SPEC-9.1, SPEC-10.1
- Dependencies: varmennettu lähdekeruu, `build_index.py`, rajattu git-commit/push ja julkisen Pages-URL:n HTTP 200 -tarkistus.
- Affected files/components: `paivan_ai_uutiset_2026-10-07.html`, `index.html`, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, branch `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`.
- External resource preflight: owner Anna Korpi / `gene8tor-AI`; billing account ei käytössä; production environment GitHub Pages; data boundary vain julkinen suomenkielinen HTML, tiivistelmät ja julkiset lähde-URL:t; rollback = revert julkaisucommit ja indeksimuutos; ei käyttöoikeus-, nimike-, laskutus- tai Pages-asetusmuutoksia; cron-payload valtuuttaa tämän rajatun julkaisun. Ei sähköpostia eikä Notion-kirjoitusta.
- Acceptance criteria: päivän HTML sisältää varmennetut AI-uutiset, AI-työkalut, Telco AI -alueosiot, X-signaalien tilan ja YouTube-osion; `build_index.py` ja `git diff --check` onnistuvat; commit sisältää vain päivän HTML:n ja indeksin; main-haaran Pages-URL palauttaa HTTP 200.
- Test expectations: HTML-rakenteen, lähde-URL:ien, `git diff --check`:n, commit-sisällön ja HTTP-vastauksen tarkistus.
- Implementation evidence: 13 varmennettua uutis-/työkalu-/Telco-nostoa ja yksi varmennettu YouTube-kuunteluvinkki; `python3 build_index.py`, HTML-jäsennys (28 ulkoista linkkiä) ja `git diff --check` PASS; commit `9e71113` pushed to `main` vain tiedostoilla `paivan_ai_uutiset_2026-10-07.html` ja `index.html`.
- Verification: PASS — julkinen URL palautti HTTP 200 viidennellä tarkistuskerralla: `https://gene8tor-ai.github.io/ai-uutiskirjeet/paivan_ai_uutiset_2026-10-07.html` (2026-10-07, Europe/Helsinki).
- Gaps / follow-up: X-haku epäonnistui virheeseen `Network request failed: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Missing Authority Key Identifier (_ssl.c:1032)`, joten X-osio sisältää vain läpinäkyvän rajoitteen. Ensisijaisten YouTube-kanavien metadatakeruu epäonnistui `yt-dlp`-komennossa virheeseen `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`; sivulla on yksi hakutuloksella varmennettu Matt Wolfe -video, eikä videoväitteitä käytetä uutisten lähteenä. Ei sähköpostia eikä Notion-kirjoitusta.

## TASK-003 — Julkaise AI Morning Brief 2026-10-06
- Status: DONE
- Implements: SPEC-3.1, SPEC-7.1, SPEC-9.1, SPEC-10.1
- Dependencies: varmennettu lähdekeruu, `build_index.py`, GitHub Pages -deploy, julkisen URL:n HTTP 200 -tarkistus.
- Affected files/components: `paivan_ai_uutiset_2026-10-06.html`, `index.html`, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, branch `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`.
- External resource preflight: owner Anna Korpi / `gene8tor-AI`; billing account ei käytössä; production environment GitHub Pages; data boundary vain julkinen suomenkielinen HTML, tiivistelmät ja julkiset lähde-URL:t; rollback = revert julkaisucommit ja indeksimuutos; ei käyttöoikeus-, nimike-, laskutus- tai Pages-asetusmuutoksia; cron-payload valtuuttaa tämän rajatun julkaisun. Ei sähköpostia eikä Notion-kirjoitusta.
- Acceptance criteria: päivän HTML sisältää varmennetut AI-uutiset, AI-työkalut, Telco AI -alueosiot, X-signaalien tilan ja YouTube-osion; `build_index.py` ja `git diff --check` onnistuvat; commit sisältää vain päivän HTML:n ja indeksin; main-haaran Pages-URL palauttaa HTTP 200.
- Test expectations: HTML-rakenteen, lähde-URL:ien, `git diff --check`:n, commit-sisällön ja HTTP-vastauksen tarkistus.
- Implementation evidence: 11 varmennettua uutis-/työkalunostoa, kolme Telco AI -aluekohtaista rajoitenostoa, X- ja YouTube-tilarajoitteet; `python3 build_index.py`, HTML-jäsennys ja `git diff --check` PASS; commit `8073a75` pushed to `main` vain tiedostoilla `paivan_ai_uutiset_2026-10-06.html` ja `index.html`.
- Verification: PASS — julkinen URL palautti HTTP 200: `https://gene8tor-ai.github.io/ai-uutiskirjeet/paivan_ai_uutiset_2026-10-06.html` (2026-10-06, Europe/Helsinki).
- Gaps / follow-up: X-haku epäonnistui virheeseen `Network request failed: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Missing Authority Key Identifier (_ssl.c:1032)`. YouTube-kanavametadata epäonnistui `yt-dlp`-komennossa virheeseen `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`; Future Tools -video tiivistettiin tutkavinkkinä, mutta videoväitteitä ei nostettu ilman ensisijaisen lähteen varmennusta. Kolme lähdeosoitetta (Axios, GeekWire, Politico) vastasi automaattiselle tarkistukselle HTTP 403, mutta osoitteet ovat lähdeaineiston alkuperäislinkkejä; niitä ei poistettu sivulta.

## TASK-001 — Julkaise AI Morning Brief 2026-10-05
- Status: DONE
- Implements: SPEC-3.1, SPEC-7.1, SPEC-9.1, SPEC-10.1
- Dependencies: lähdekeruu, `build_index.py`, GitHub Pages -deploy
- Affected files/components: `paivan_ai_uutiset_2026-10-05.html`, `index.html`, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`
- External resource preflight: owner Anna Korpi / gene8tor-AI; billing account ei käytössä; production environment GitHub Pages; data boundary vain julkinen HTML ja julkiset lähde-URL:t; rollback = revert julkaisucommit tai poista uusi linkki seuraavassa commitissa; no access, naming, billing or Pages-config changes; cron payload authorizes this bounded publication.
- Acceptance criteria: päivän HTML sisältää pyydetyt osiot, indeksi rakentuu, `git diff --check` läpäisee, pushataan vain rajatut tiedostot ja julkinen URL palauttaa HTTP 200.
- Test expectations: HTML-osioiden, lähde-URL:ien, git-diffin ja HTTP-vastauksen tarkistus.
- Implementation evidence: commit `a7d4bf9` pushed to `main`; `python3 build_index.py` and `git diff --check` PASS; 15 article cards, 15 unique external URLs, zero placeholder URLs.
- Verification: PASS — OpenClaw web fetch observed HTTP 200 and title `AI Morning Brief – 5. lokakuuta 2026` at `https://gene8tor-ai.github.io/ai-uutiskirjeet/paivan_ai_uutiset_2026-10-05.html` on 2026-10-05 03:05:56 UTC.
- Gaps / follow-up: X-haun SSL-varmennevirhe; YouTube-kanavahaku SSL-varmennevirhe. Julkaistu osioissa läpinäkyvinä rajoitteina; ei sisältöä keksitty.

## TASK-002 — Julkaise AI-työkalujen ja tuotejulkaisujen katsaus 2026-10-05
- Status: DONE
- Implements: SPEC-3.2, SPEC-7.1, SPEC-7.2, SPEC-9.1, SPEC-10.1
- Dependencies: ensisijaisten lähteiden tarkistus, Future Tools -videon tiivistys, `build_index.py`, GitHub Pages -deploy, HTTP 200 -varmistus, Gmail API -päiväraja.
- Affected files/components: `newsletters/ai_tyokalut_uutiset_2026-10-05.html`, `ai-website/ai_tyokalut_uutiset_2026-10-05.html`, `ai-website/index.html`, GitHub repository `gene8tor-AI/ai-uutiskirjeet`, `main`, GitHub Pages `https://gene8tor-ai.github.io/ai-uutiskirjeet/`, Gmail API sender script.
- External resource preflight: owner Anna Korpi / gene8tor-AI; billing account ei käytössä; production environment GitHub Pages `gene8tor-ai.github.io/ai-uutiskirjeet`; data boundary vain julkinen suomenkielinen HTML ja julkiset lähde-URL:t; rollback = revert uusi julkaisucommit ja indeksi tai julkaisucommitin palautus; sähköposti sisältää vain URL:n, otsikon ja lyhyen johdannon Sami.sikila@teliacompany.comille; ei pääsy-, nimike-, laskutus- tai Pages-asetusmuutoksia; cron payload valtuuttaa tämän rajatun julkaisun ja yhden Gmail API -lähetysyrityksen.
- Acceptance criteria: 9 varmennettua nostoa, molemmat HTML-kopiot, `python3 build_index.py`, `git diff --check`, vain uusi HTML ja `index.html` commitissa/pushissa, Pages HTTP 200 ennen Gmail API -komentoa; lähettäjän tila tallennetaan.
- Test expectations: lähde- ja päivämäärärajauksen tarkistus, HTML-linkkien tarkistus, index-build, diff-check, git-push, HTTP-status ja lähettäjäkomennon tulos.
- Implementation evidence: 9 ensisijaista valmistajalähdettä tarkistettu; Future Tools -video `dDgncbBAA0c` tiivistetty komennolla `summarize --youtube auto --length medium`; paikalliset HTML-kopiot luotu; `python3 build_index.py` ja `git diff --check` PASS; commit `3a26de3` pushed to `main` (vain `ai_tyokalut_uutiset_2026-10-05.html` ja `index.html`); Pages-URL palautti HTTP 200. Gmail API -komento palautti `SKIPPED`, koska 2026-10-05 lähetyspaikka oli jo käytetty.
- Verification: PASS — julkaisu ja HTTP 200 varmennettu; päiväkohtainen sähköpostiraja noudatettu ilman vaihtoehtoista lähetysyritystä.
- Gaps / follow-up: YouTube-kanavasivun haku epäonnistui paikallisen SSL-varmennevirheen vuoksi; video löytyi varareitillä ja tiivistettiin. Video ei ole katsauksen pääasiallinen lähde. Sähköpostia ei lähetetty tässä ajossa, koska lähettäjä varasi/raportoi päivän paikan jo käytetyksi.
