# SPEC — AI-uutiskirjeet GitHub Pages

Status: Approved
Owner: Anna Korpi
Last reviewed: 2026-10-05

## SPEC-1 Product vision
### SPEC-1.1 Julkinen aamukatsaus
- Intent: julkaista päivittäin lähdekriittinen suomenkielinen AI Morning Brief GitHub Pagesissa.
- Success signal: päivän sivu on julkisesti luettavissa HTTP 200 -vastauksella.

## SPEC-3 Functional requirements
### SPEC-3.1 Päivän AI Morning Brief
- The product must: julkaista yksi tai useampi HTML-katsaus samalla Helsinki-kalenteripäivällä, jossa ovat varmennetut AI-uutiset, työkalut, Telco AI alueittain, X-signaalien tila ja YouTube-osio. Saman päivän lisäjulkaisu käyttää yksilöivää, päiväysalkuista tiedostonimeä; hyväksytty tarkenne on yksittäinen pieni kirjain, esimerkiksi `_b`.
- Acceptance criteria:
  - GIVEN 2026-10-05 ajo WHEN julkaisu valmistuu THEN `paivan_ai_uutiset_2026-10-05.html` sisältää kaikki osiot ja lähdelinkit.
  - GIVEN julkaisu on pushattu main-haaraan WHEN julkinen URL tarkistetaan THEN se palauttaa HTTP 200.
- Errors and edge cases: jos X- tai YouTube-haku ei tuota varmennettuja tuloksia, osio kertoo rajoitteen eikä keksi sisältöä.
- Links: TASK-001.

### SPEC-3.2 Viikoittainen AI-työkalujen ja tuotejulkaisujen katsaus
- Intent: julkaista maanantaisin lähdekriittinen suomenkielinen katsaus enintään kuusi päivää vanhoista, työelämän kannalta merkittävistä AI-työkalu- ja tuotejulkaisuista.
- The product must: sisältää vain alkuperäislähteellä varmennetut nostot, ryhmitellä ne työkaluihin ja tuotteisiin, automaatioon ja integraatioihin, kehittäjätyöhön sekä dataan, hallintaan ja tietoturvaan. Future Tools -video on tutkavinkki, ei ensisijainen lähde.
- Acceptance criteria:
  - GIVEN 2026-10-05 ajo WHEN julkaisu valmistuu THEN `ai_tyokalut_uutiset_2026-10-05.html` on molemmissa määritellyissä paikallisissa kohteissa, sisältää lähdelinkit ja enintään 100 sanan johdannon.
  - GIVEN main-haaran julkaisu WHEN julkinen URL tarkistetaan THEN se palauttaa HTTP 200.
  - GIVEN HTTP 200 -varmennus WHEN päivittäinen Gmail API -lähetysvaraus tehdään THEN vain `send_news_link_once.py`-komentoa käytetään; SENT-, SKIPPED- tai virhetila kirjataan.
- Failure behavior: jos video tai julkaisuajankohta ei varmistu, sisältö jätetään pois ja rajoite kerrotaan. Jos Gmail-lähettäjä palauttaa SKIPPED tai virheen, muita sähköpostireittejä eikä saman päivän uutta yritystä käytetä.
- Links: TASK-002.

### SPEC-3.3 Viikon AI-uutiskuva
- Intent: julkaista yksi lähdekriittinen, toimituksellinen AI-uutiskuva merkittävästä enintään seitsemän päivää vanhasta AI-uutisesta.
- The product must: sisältää yhden alkuperäislähteellä varmennetun uutisen, suomenkielisen HTML-tiivistelmän, toimituksellisen kuvituksen ilman tunnistettavia henkilöitä, logoja, kuvatekstiä tai vesileimaa sekä julkisen lähdelinkin.
- Acceptance criteria:
  - GIVEN sopiva uutinen löytyy WHEN julkaisu valmistuu THEN `viikon_ai_uutiskuva_YYYY-MM-DD.html` ja siihen viittaava kuva ovat GitHub Pages -julkaisussa.
  - GIVEN main-haaran julkaisu WHEN julkinen URL tarkistetaan THEN HTML-sivu palauttaa HTTP 200.
  - GIVEN HTTP 200 -varmennus WHEN Gmail API -päiväraja tarkistetaan THEN vain `send_news_link_once.py`-komentoa käytetään ja SENT-, SKIPPED- tai virhetila kirjataan.
- Failure behavior: jos enintään seitsemän päivää vanhaa, alkuperäislähteellä varmennettua merkittävää uutista ei löydy, mitään ei julkaista eikä lähetetä.
- Links: TASK-006.

### SPEC-3.4 Telco-sektorin AI-päiväkatsaus
- Intent: julkaista lähdekriittinen, suomenkielinen Telco-sektorin AI-katsaus GitHub Pagesissa.
- The product must: käyttää viimeisten seitsemän päivän Gmail- ja Notion-lukulähteitä, valita vain televiestintäalaan olennaisesti liittyvät AI-uutiset ja ryhmitellä ne US-, Euroopan- ja Aasian telco-osioihin. Jokaisella nostolla on julkinen alkuperäislähdelinkki.
- Acceptance criteria:
  - GIVEN ajantasaiset lähteet WHEN katsaus valmistuu THEN `telco_ai_uutiset_YYYY-MM-DD.html` sisältää vain telco-AI-aiheisia, suomenkielisiä nostoja ja aluejaon.
  - GIVEN julkaisu on pushattu main-haaraan WHEN julkinen URL tarkistetaan THEN se palauttaa HTTP 200.
  - GIVEN HTTP 200 -varmennus WHEN päivittäinen Gmail API -lähetysvaraus tehdään THEN vain `send_news_link_once.py`-komentoa käytetään; SENT-, SKIPPED- tai virhetila kirjataan.
- Failure behavior: jos alueelta ei löydy lähdekriteerit täyttävää nostoa, osio kertoo tämän eikä lisää epäolennaista sisältöä. Jos Gmail-lähettäjä palauttaa SKIPPED tai virheen, muita sähköpostireittejä eikä saman päivän uutta yritystä käytetä.
- Links: TASK-009.

### SPEC-3.5 Käyttäjän pyytämä Hot News
- Intent: julkaista käyttäjän nimenomaisesti nimeämästä Hot News -lähde-URL:sta yksi lähdekriittinen, suomenkielinen hälytys sekä toimittaa sen linkki sähköpostikanavaan.
- The product must: käyttää käyttäjän antamaa alkuperäis- tai luotettavaa lähdettä, erottaa yhtiön tavoitteet toteutuneista luvuista, julkaista yksittäisen HTML-sivun päivä- ja kellonaikaleimallisella `hot_news_YYYY-MM-DD_HHMM.html`-nimellä ja varmentaa julkinen URL HTTP 200 -vastauksella.
- Acceptance criteria:
  - GIVEN käyttäjän viestissä on ilmaisu `Hot news` ja URL WHEN lähde on luettu THEN sivu sisältää suomenkielisen otsikon, 2–4 lauseen yhteenvedon, alkuperäislinkin ja lähteestä varmennetut faktat.
  - GIVEN sivu on julkaistu WHEN URL tarkistetaan THEN se palauttaa HTTP 200 ennen Gmail API -lähetystä.
  - GIVEN julkinen URL on varmennettu WHEN Hot News on käyttäjän nimenomaisesti pyytämä THEN `send_news_link_once.py` kirjaa lähetysyrityksen SPEC-7.2:n enintään kolmen yrityksen päivärajassa.
- Failure behavior: jos lähdettä ei voi lukea tai julkinen URL ei palaudu HTTP 200, sivua ei lähetetä. Gmail API -virhe jää päivän yrityshistoriaan eikä sitä kierretä muulla lähetysreitillä.
- Links: TASK-011.

## SPEC-7 Integrations
### SPEC-7.1 GitHub Pages
- Purpose: hostata julkinen HTML osoitteessa `https://gene8tor-ai.github.io/ai-uutiskirjeet/`.
- Data exchanged: vain julkaisusivun HTML, otsikot, tiivistelmät ja julkiset lähde-URL:t.
- Failure behavior: ei väitetä julkaisua onnistuneeksi ilman HTTP 200 -varmistusta.

### SPEC-7.2 Päivärajoitettu Gmail API -linkkilähetys
- Purpose: toimittaa sovittuun vastaanottajaan enintään yksi lyhyt plain-text-linkki per Europe/Helsinki-kalenteripäivä julkisen URL:n HTTP 200 -varmennuksen jälkeen.
- Data exchanged: julkinen URL, lyhyt otsikko ja suomenkielinen johdanto; vastaanottaja `Sami.sikila@teliacompany.com`.
- Failure behavior: lähettäjän atominen päivävaraus laskee kaikki Gmail API -lähetysyritykset. Enintään yksi yritys on sallittu per päivä; SKIPPED tai virhe ei käynnistä vaihtoehtoista lähetystä. Jokainen yritys ja sen tulos säilytetään päivän lähetysvarauksen historiassa.

### SPEC-7.3 Notion-uutismetatieto
- Purpose: tallentaa julkaistun uutiskuvan lähde, julkaisu-URL ja toimituksellinen tiivistelmä sovittuun uutistietokantaan.
- Data exchanged: uutisotsikko, julkaisupäivä, alkuperäislähde-URL, julkinen Pages-URL ja lyhyt suomenkielinen kuvaus.
- Failure behavior: metadatan tallennus varmennetaan lukemalla luotu tietue; epäonnistuminen pidetään tehtävässä näkyvänä ennen kuin julkaisu merkitään täysin varmennetuksi.

## SPEC-9 Acceptance criteria
### SPEC-9.1 Julkaisun varmennus
- HTML validoituu rakenteellisesti, `build_index.py` ja `git diff --check` onnistuvat, commit on main-haarassa ja julkinen sivu vastaa HTTP 200.

## SPEC-10 Constraints
### SPEC-10.1 Ajokohtaiset rajat
- Kaikki automaattiset uutisjulkaisut voivat käyttää ainoastaan `send_news_link_once.py`-Gmail API -lähettäjää HTTP 200 -varmennuksen jälkeen; vastaanottajalle tehdään enintään yksi lähetysyritys per Europe/Helsinki-kalenteripäivä. SMTP, smtplib, email-skill ja muut suorat sähköpostireitit ovat kiellettyjä. Notion-kirjoitusta ei tehdä.
- Poikkeus Viikon AI-uutiskuvalle (SPEC-3.3): ajon nimenomainen toimitusraja voi edellyttää SPEC-7.3:n mukaista suppeaa Notion-metatietoa. Kirjoitus sisältää vain otsikon, julkaisupäivän, alkuperäislähde-URL:n, Pages-URL:n ja lyhyen suomenkielisen kuvauksen, ja tietue luetaan takaisin varmennusta varten.
- X- ja YouTube-väitteet esitetään vain varmennettuina tai rajoitteena.
- AI-työkalukatsauksessa sähköposti lähetetään vain SPEC-7.2:n Gmail API -rajauksella, ei SMTP:llä tai muulla suoralla sähköpostireitillä.
- Viikon AI-uutiskuva käyttää vain aiheetonta toimituskuvitusta: ei tunnistettavia henkilöitä, logoja, tekstielementtejä, kuvatekstiä eikä vesileimaa.

## SPEC-11 Out of scope
### SPEC-11.1 Ei muuta infrastruktuuria
- Ei muutoksia GitHub Pages -asetuksiin, omistajuuteen, laskutukseen tai käyttöoikeuksiin.

## Change log
- 2026-10-14 — SPEC-10.1: täsmennetty Viikon AI-uutiskuvan Notion-metatietopoikkeus ja yhteinen yhden Gmail API -yrityksen päiväkohtainen raja.
- 2026-10-10 — SPEC-3.5: lisätty käyttäjän nimenomaisesti pyytämä Hot News -kulku, julkaisun/lähetyksen varmennukset ja kolmen Gmail API -yrityksen päivärajauksen käyttö.
- 2026-10-09 — SPEC-3.1, SPEC-7.2, SPEC-10.1: hyväksytty yhden pienen kirjainsuffiksin käyttö saman päivän lisäkatsauksessa ja käyttäjä hyväksyi enintään kolme Gmail API -lähetysyritystä per Helsinki-päivä; yrityshistoria säilytetään atomisessa päivävarauksessa.
- 2026-10-07 — SPEC-3.1, SPEC-7.2, SPEC-10.1: päivitetty ajokohtainen raja sallimaan useat päiväysalkuiset julkaisut samalla Helsinki-päivällä sekä rajaamaan linkkisähköposti yhteiseen Gmail API -lähettäjään ja yhteen yritykseen per päivä.
- 2026-10-07 — SPEC-3.3, SPEC-7.3, SPEC-10.1: lisätty rajattu Viikon AI-uutiskuvan julkaisukulku, kuvitusraja ja Notion-metatieto.
- 2026-10-06 — SPEC-3.1: Päivän ajon yksilöity julkaisukohde on `paivan_ai_uutiset_2026-10-06.html`; sisältöön kootaan vain varmennetut lähteet, ja X- sekä YouTube-rajoitteet esitetään näkyvästi.
- 2026-10-05 — SPEC-3.1: Lisätty rajattu AI Morning Brief -julkaisun hallintamäärittely ennen Pages-päivitystä.

## SPEC-3.6 Public original-source RSS (approved request 2026-10-24, topic35 msg3737)
- Publish `feeds/ai-news.xml`, RSS 2.0, from the same ten public RSS/Atom sources as loitsu-news-ingestion production secret version 2. This is a separate read-only export, not the private Notion database and not an AI digest.
- Preserve source article titles, article links (including source-provided Google News redirects), real publication dates, source attribution and source-provided snippets/images. Never invent publication times, images or full article text. No translation or generated summaries. Images are optional where the upstream feed and public article preview metadata supply none.
- ASSUMPTION-RSS-1: dashboard history retains up to 100 unique original URLs from the previous 7 days, newest first, up to 10 per source per run; the Notion 24-hour/25-item ingestion limits remain unchanged. Prior successfully fetched entries may be retained within the window on source failure.
- Refresh 3 times daily using a bounded dependency-free GitHub Actions workflow on this existing public Pages repository. Run times 03:25,10:25,16:25 UTC (GitHub may delay schedules). Public-source configuration is versioned; changes to ingestion sources must also update the export registry. No cloud secrets, Notion token, private data or email access.
- Source errors are reported in `feeds/status.json`; total outage/zero eligible results fails without overwriting the last good feed. Individual source failure must not erase previously valid items within retention. No credentials are required by RSS readers.
- Acceptance: tests cover RSS/Atom, original content preservation, optional thumbnails, safe XML/HTML/URL handling, stable IDs, freshness/deduplication and failure recovery; live URL HTTP200 and valid RSS with matching published bytes; an actual Actions refresh passes and its Pages publication is verified. start.me account rendering is separately NOT TESTED unless inspected in that app.
- SPEC-7.1 data boundary extends to public RSS XML, source metadata and public refresh status; SPEC-11.1 remains unchanged for Pages settings, IAM, ownership and billing.

### SPEC-3.6.1 Article preview images (approved 2026-10-24, Anna topic35 msg3773)
- Extend the same public RSS URL with publisher-provided article preview images when the upstream RSS/Atom item has no image. Prefer existing feed images; otherwise read only public article HTML Open Graph or Twitter image metadata, without login, paywall/bot bypass, AI images, stock substitutes or full-article storage.
- Google News wrappers may be resolved through their public article URL-resolution response solely to reach the publisher for metadata; never use the generic Google News logo/preview as the article image. Preserve original feed article links, titles, dates, attribution and GUIDs unchanged.
- ASSUMPTION-RSS-IMG-1: 4 concurrent workers, at most 100 selected articles, 90-second enrichment admission budget, 8-second per-request timeout, 1 MiB HTML/response read cap and 5 redirects. Reuse previous fresh image URLs for the same original article URL; retries occur at later regular refreshes. A failed image lookup never removes an article or fails a successful feed refresh.
- Only safe public HTTPS image URLs are syndicated as media:thumbnail and description img; article requests/redirects reject non-public destinations. No image binaries, cookies, credentials or page bodies are stored. No new source registry, paid dependency, cloud/Notion/IAM/scheduler change.
- Acceptance: deterministic tests for direct/relative OG and Twitter metadata, Google wrapper resolution without logo substitution, existing-image precedence/reuse, unsafe destinations/redirects, request and global limits, malformed/failed lookup fallback and stable original metadata; public refreshed XML contains real preview-image URLs and validates as RSS; inspect actual start.me image rendering, or keep that criterion PARTIAL.
- Links: TASK-RSS-002, DEC-RSS-002; supersedes only TASK-RSS-001's no-article-metadata-scraping limitation.

### SPEC-3.8 AI:sta arvoa (approved24Oct2026)
- Publish twice-weekly Finnish original-source editorial analysis about practical AI adoption, people/leadership, end-to-end processes, scaling and measured benefits. Title AI:sta arvoa — Työn muutoksesta skaalautuvaan hyötyyn. About600–900words; one actionable issue, not product-news aggregation. Current public Pages, no email/Notion or hosting changes. Prefix ai_arvoa_YYYY-MM-DD.html.
- Every issue actively searches Finnish/English web, opens original sources and differentiates measured evidence/guidance/vendor claims/illustrative examples. Fresh evidence date within30days; older research explicitly background, never new news. Skip if no meaningful new topic.
- Before publication compare whole archive semantically, including earlier MorningBrief/other issues. Repeated topic/claim needs material new evidence and explicit what-changed/prior coverage. Structured topic/fact ledger guards repetition, does not replace editorial judgment. Exact URL novelty alone insufficient.
- Acceptance: tested input/duplicate/source-overlap guards; escaped accessible HTML and index entry; reviewed pushed source; one actual public trial HTTP200 matching merged bytes. Scheduling Tue/Thu11Helsinki only after trial PASS; report URL/novelty/sources/commit, never scheduler success as content proof.
- Links TASK-ARVOA-001, docs/ai-arvoa.md. Existing source/hosting boundaries preserved. No confidential business data in publication or ledger.

#### SPEC-3.8.1 Multi-item digest revision (approved24Oct2026, supersedes single-theme format)
-3–5distinct fresh items each issue, each independently states new evidence, impact on work/people/leadership/processes, demonstrated/claimed/unknown benefit and evidence limits. Finish actionable synthesis; no padding to reach count. If fewer than3novel verified items, skip.
- Each item is novelty-checked against all prior Pages articles and individual entries in every digest; legacy single-topic history retained. New topicIDs alone never make used evidence new. Do not split one source into multiple stories.
- New writes use digest-v2 schema. Explicitly requested extra same-day trial uses edition b /ai_arvoa_YYYY-MM-DD_b.html; preserve previousHTML/JSON byte-identically. Normal scheduler skips any edition already published today. Title/cadence/source/privacy/noemail boundaries unchanged. Tests cover count, per-item freshness and duplicate history across both formats, repeat claims, distinct items and edition filenames.
- TASK-ARVOA-002 / issue#8.
