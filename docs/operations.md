# AI-uutiskirjeet: julkaisu ja ylläpito

## Palvelu

| Asia | Tieto |
| --- | --- |
| Tuotanto-URL | `https://gene8tor-ai.github.io/ai-uutiskirjeet/` |
| Lähdekoodi | `gene8tor-AI/ai-uutiskirjeet` |
| Alusta | GitHub Pages |
| Julkaisulähde | `main`-haara |
| Sisällön tuotanto | OpenClaw-työtilan uutistyönkulut |

## Normaali julkaisukulku

1. Tuota HTML-julkaisu soveltuvalla uutistyönkululla.
2. Tallenna se repoon sovitulla tiedostonimellä, esimerkiksi `paivan_ai_uutiset_YYYY-MM-DD.html` tai `hot_news_YYYY-MM-DD_HHMM.html`.
3. Päivitä indeksi:

   ```bash
   python3 build_index.py
   ```

4. Tarkista muutokset ennen committia:

   ```bash
   git status --short
   git diff --check
   ```

5. Committoi ja pushaa `main`-haaraan. Varmista julkaisu tuotanto-URL:sta.

## Vianrajaus

- **Uusi julkaisu ei näy:** varmista, että HTML-tiedosto ja `index.html` ovat `main`-haarassa ja GitHub Pagesin julkaisu on onnistunut.
- **Indeksistä puuttuu julkaisu:** aja `build_index.py` uudelleen ja tarkista tiedostonimi.
- **Linkki ei toimi:** tarkista, että tiedosto on repositorion juuressa ja että linkki käyttää täsmälleen samaa tiedostonimeä.

## Turvallisuus ja rajat

- Älä tallenna tähän repositorioon API-avaimia, SMTP-tunnuksia tai henkilökohtaisia tietoja.
- Julkaisuarkisto on julkinen. Varmista ennen pushia, että sisältö on tarkoitettu julkisesti nähtäväksi.
- Varsinaiset sähköposti- ja uutislähdeasetukset kuuluvat OpenClaw-työtilaan.
