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
- The product must: julkaista yksi HTML-katsaus, jossa ovat varmennetut AI-uutiset, työkalut, Telco AI alueittain, X-signaalien tila ja YouTube-osio.
- Acceptance criteria:
  - GIVEN 2026-10-05 ajo WHEN julkaisu valmistuu THEN `paivan_ai_uutiset_2026-10-05.html` sisältää kaikki osiot ja lähdelinkit.
  - GIVEN julkaisu on pushattu main-haaraan WHEN julkinen URL tarkistetaan THEN se palauttaa HTTP 200.
- Errors and edge cases: jos X- tai YouTube-haku ei tuota varmennettuja tuloksia, osio kertoo rajoitteen eikä keksi sisältöä.
- Links: TASK-001.

## SPEC-7 Integrations
### SPEC-7.1 GitHub Pages
- Purpose: hostata julkinen HTML osoitteessa `https://gene8tor-ai.github.io/ai-uutiskirjeet/`.
- Data exchanged: vain julkaisusivun HTML, otsikot, tiivistelmät ja julkiset lähde-URL:t.
- Failure behavior: ei väitetä julkaisua onnistuneeksi ilman HTTP 200 -varmistusta.

## SPEC-9 Acceptance criteria
### SPEC-9.1 Julkaisun varmennus
- HTML validoituu rakenteellisesti, `build_index.py` ja `git diff --check` onnistuvat, commit on main-haarassa ja julkinen sivu vastaa HTTP 200.

## SPEC-10 Constraints
### SPEC-10.1 Ajokohtaiset rajat
- Ei sähköpostia eikä Notion-kirjoitusta.
- X- ja YouTube-väitteet esitetään vain varmennettuina tai rajoitteena.

## SPEC-11 Out of scope
### SPEC-11.1 Ei muuta infrastruktuuria
- Ei muutoksia GitHub Pages -asetuksiin, omistajuuteen, laskutukseen tai käyttöoikeuksiin.

## Change log
- 2026-10-05 — SPEC-3.1: Lisätty rajattu AI Morning Brief -julkaisun hallintamäärittely ennen Pages-päivitystä.
