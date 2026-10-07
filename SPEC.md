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
- The product must: julkaista yksi tai useampi HTML-katsaus samalla Helsinki-kalenteripäivällä, jossa ovat varmennetut AI-uutiset, työkalut, Telco AI alueittain, X-signaalien tila ja YouTube-osio. Saman päivän lisäjulkaisu käyttää yksilöivää, päiväysalkuista tiedostonimeä.
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

## SPEC-7 Integrations
### SPEC-7.1 GitHub Pages
- Purpose: hostata julkinen HTML osoitteessa `https://gene8tor-ai.github.io/ai-uutiskirjeet/`.
- Data exchanged: vain julkaisusivun HTML, otsikot, tiivistelmät ja julkiset lähde-URL:t.
- Failure behavior: ei väitetä julkaisua onnistuneeksi ilman HTTP 200 -varmistusta.

### SPEC-7.2 Päivärajoitettu Gmail API -linkkilähetys
- Purpose: toimittaa sovittuun vastaanottajaan yksi lyhyt plain-text-linkki per Europe/Helsinki-kalenteripäivä julkisen URL:n HTTP 200 -varmennuksen jälkeen.
- Data exchanged: julkinen URL, lyhyt otsikko ja suomenkielinen johdanto; vastaanottaja `Sami.sikila@teliacompany.com`.
- Failure behavior: lähettäjän atominen päivävaraus on ratkaiseva; SKIPPED tai virhe ei käynnistä vaihtoehtoista lähetystä tai uutta yritystä samana päivänä.

### SPEC-7.3 Notion-uutismetatieto
- Purpose: tallentaa julkaistun uutiskuvan lähde, julkaisu-URL ja toimituksellinen tiivistelmä sovittuun uutistietokantaan.
- Data exchanged: uutisotsikko, julkaisupäivä, alkuperäislähde-URL, julkinen Pages-URL ja lyhyt suomenkielinen kuvaus.
- Failure behavior: metadatan tallennus varmennetaan lukemalla luotu tietue; epäonnistuminen pidetään tehtävässä näkyvänä ennen kuin julkaisu merkitään täysin varmennetuksi.

## SPEC-9 Acceptance criteria
### SPEC-9.1 Julkaisun varmennus
- HTML validoituu rakenteellisesti, `build_index.py` ja `git diff --check` onnistuvat, commit on main-haarassa ja julkinen sivu vastaa HTTP 200.

## SPEC-10 Constraints
### SPEC-10.1 Ajokohtaiset rajat
- Päivän AI Morning Brief voi käyttää ainoastaan `send_news_link_once.py`-Gmail API -lähettäjää HTTP 200 -varmennuksen jälkeen; enintään yksi lähetysyritys vastaanottajalle per Europe/Helsinki-kalenteripäivä. SMTP, smtplib ja muut suorat sähköpostireitit ovat kiellettyjä. Notion-kirjoitusta ei tehdä.
- X- ja YouTube-väitteet esitetään vain varmennettuina tai rajoitteena.
- AI-työkalukatsauksessa sähköposti lähetetään vain SPEC-7.2:n Gmail API -rajauksella, ei SMTP:llä tai muulla suoralla sähköpostireitillä.
- Viikon AI-uutiskuva käyttää vain aiheetonta toimituskuvitusta: ei tunnistettavia henkilöitä, logoja, tekstielementtejä, kuvatekstiä eikä vesileimaa.

## SPEC-11 Out of scope
### SPEC-11.1 Ei muuta infrastruktuuria
- Ei muutoksia GitHub Pages -asetuksiin, omistajuuteen, laskutukseen tai käyttöoikeuksiin.

## Change log
- 2026-10-07 — SPEC-3.1, SPEC-7.2, SPEC-10.1: päivitetty ajokohtainen raja sallimaan useat päiväysalkuiset julkaisut samalla Helsinki-päivällä sekä rajaamaan linkkisähköposti yhteiseen Gmail API -lähettäjään ja yhteen yritykseen per päivä.
- 2026-10-07 — SPEC-3.3, SPEC-7.3, SPEC-10.1: lisätty rajattu Viikon AI-uutiskuvan julkaisukulku, kuvitusraja ja Notion-metatieto.
- 2026-10-06 — SPEC-3.1: Päivän ajon yksilöity julkaisukohde on `paivan_ai_uutiset_2026-10-06.html`; sisältöön kootaan vain varmennetut lähteet, ja X- sekä YouTube-rajoitteet esitetään näkyvästi.
- 2026-10-05 — SPEC-3.1: Lisätty rajattu AI Morning Brief -julkaisun hallintamäärittely ennen Pages-päivitystä.
