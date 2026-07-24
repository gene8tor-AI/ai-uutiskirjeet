# AI-uutiskirjeet

Julkaisuarkisto Loitsu Labsin AI-uutiskirjeille ja Hot News -nostoille.

**Tuotanto:** <https://gene8tor-ai.github.io/ai-uutiskirjeet/>

## Tarkoitus

Repositorio sisältää julkaistut HTML-katsaukset sekä niiden indeksisivun. Sisältö syntyy OpenClaw-työnkuluissa ja julkaistaan GitHub Pagesiin.

Tämä repo on julkaisuarkisto – uutisten haku-, analyysi- ja sähköpostilogiikka pidetään OpenClaw-työtilan skill- ja script-rakenteissa, ei täällä.

## Rakenne

- `index.html` – julkaisuarkiston etusivu
- `build_index.py` – indeksin muodostus julkaistuista HTML-tiedostoista
- `*.html` – yksittäiset uutiskirjeet ja Hot News -julkaisut
- `docs/operations.md` – julkaisu- ja ylläpito-ohje

## Julkaisuperiaate

1. Uutiskirjeen työnkulku muodostaa HTML-tiedoston tähän repositorioon.
2. `build_index.py` päivittää indeksin.
3. Muutokset validoidaan ja commit/push tehdään `main`-haaraan.
4. GitHub Pages julkaisee tuotantosivun.

Älä tallenna tähän repositorioon tunnuksia, API-avaimia tai sähköpostiasetuksia.

## Lisätiedot

Katso [ylläpito-ohje](docs/operations.md).
