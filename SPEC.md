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
- Purpose: toimittaa sovittuun vastaanottajaan enintään kolme lyhyttä plain-text-linkkiä per Europe/Helsinki-kalenteripäivä julkisen URL:n HTTP 200 -varmennuksen jälkeen.
- Data exchanged: julkinen URL, lyhyt otsikko ja suomenkielinen johdanto; vastaanottaja `Sami.sikila@teliacompany.com`.
- Failure behavior: lähettäjän atominen päivävaraus laskee kaikki Gmail API -lähetysyritykset. Enintään kolme yritystä on sallittu per päivä; SKIPPED tai virhe ei käynnistä vaihtoehtoista lähetystä. Jokainen yritys ja sen tulos säilytetään päivän lähetysvarauksen historiassa.

### SPEC-7.3 Notion-uutismetatieto
- Purpose: tallentaa julkaistun uutiskuvan lähde, julkaisu-URL ja toimituksellinen tiivistelmä sovittuun uutistietokantaan.
- Data exchanged: uutisotsikko, julkaisupäivä, alkuperäislähde-URL, julkinen Pages-URL ja lyhyt suomenkielinen kuvaus.
- Failure behavior: metadatan tallennus varmennetaan lukemalla luotu tietue; epäonnistuminen pidetään tehtävässä näkyvänä ennen kuin julkaisu merkitään täysin varmennetuksi.

## SPEC-9 Acceptance criteria
### SPEC-9.1 Julkaisun varmennus
- HTML validoituu rakenteellisesti, `build_index.py` ja `git diff --check` onnistuvat, commit on main-haarassa ja julkinen sivu vastaa HTTP 200.

## SPEC-10 Constraints
### SPEC-10.1 Ajokohtaiset rajat
- Päivän AI Morning Brief voi käyttää ainoastaan `send_news_link_once.py`-Gmail API -lähettäjää HTTP 200 -varmennuksen jälkeen; enintään kolme lähetysyritystä vastaanottajalle per Europe/Helsinki-kalenteripäivä. SMTP, smtplib ja muut suorat sähköpostireitit ovat kiellettyjä. Notion-kirjoitusta ei tehdä.
- X- ja YouTube-väitteet esitetään vain varmennettuina tai rajoitteena.
- AI-työkalukatsauksessa sähköposti lähetetään vain SPEC-7.2:n Gmail API -rajauksella, ei SMTP:llä tai muulla suoralla sähköpostireitillä.
- Viikon AI-uutiskuva käyttää vain aiheetonta toimituskuvitusta: ei tunnistettavia henkilöitä, logoja, tekstielementtejä, kuvatekstiä eikä vesileimaa.

## SPEC-11 Out of scope
### SPEC-11.1 Ei muuta infrastruktuuria
- Ei muutoksia GitHub Pages -asetuksiin, omistajuuteen, laskutukseen tai käyttöoikeuksiin.

## Change log
- 2026-10-10 — SPEC-3.5: lisätty käyttäjän nimenomaisesti pyytämä Hot News -kulku, julkaisun/lähetyksen varmennukset ja kolmen Gmail API -yrityksen päivärajauksen käyttö.
- 2026-10-09 — SPEC-3.1, SPEC-7.2, SPEC-10.1: hyväksytty yhden pienen kirjainsuffiksin käyttö saman päivän lisäkatsauksessa ja käyttäjä hyväksyi enintään kolme Gmail API -lähetysyritystä per Helsinki-päivä; yrityshistoria säilytetään atomisessa päivävarauksessa.
- 2026-10-07 — SPEC-3.1, SPEC-7.2, SPEC-10.1: päivitetty ajokohtainen raja sallimaan useat päiväysalkuiset julkaisut samalla Helsinki-päivällä sekä rajaamaan linkkisähköposti yhteiseen Gmail API -lähettäjään ja yhteen yritykseen per päivä.
- 2026-10-07 — SPEC-3.3, SPEC-7.3, SPEC-10.1: lisätty rajattu Viikon AI-uutiskuvan julkaisukulku, kuvitusraja ja Notion-metatieto.
- 2026-10-06 — SPEC-3.1: Päivän ajon yksilöity julkaisukohde on `paivan_ai_uutiset_2026-10-06.html`; sisältöön kootaan vain varmennetut lähteet, ja X- sekä YouTube-rajoitteet esitetään näkyvästi.
- 2026-10-05 — SPEC-3.1: Lisätty rajattu AI Morning Brief -julkaisun hallintamäärittely ennen Pages-päivitystä.
