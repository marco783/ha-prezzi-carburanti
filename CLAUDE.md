# CLAUDE.md

Custom integration Home Assistant `prezzi_carburanti`: prezzi medi dei carburanti (benzina, gasolio, GPL, metano) da mappacarburanti.it, a livello nazionale, di provincia o di città. Distribuita via HACS.

## Struttura

Layout HACS standard: `hacs.json`, `README.md` e questo file alla root; il codice in `custom_components/prezzi_carburanti/` (percorsi sotto relativi a quella cartella).

- `const.py` — dominio, URL API, scope (`national` / `provincia` / `citta`), `FUEL_TYPES` (chiave → nome, icona).
- `config_flow.py` — step `user` (scelta scope) → step `location` (slug preso dalla sitemap). `unique_id` = `scope` oppure `scope:slug`.
- `coordinator.py` — `DataUpdateCoordinator`, polling ogni 6h. `_normalize()` riduce le forme diverse dell'API a un'unica struttura:
  `{"fuels": {fuel: {avg, min, max, count}}, "date", "source", "location": {name, region}}`.
- `sensor.py` — un `FuelPriceSensor` per carburante presente nella risposta; stato = `avg` in EUR/L, attributi in italiano (`min`, `max`, `stazioni_rilevate`, `localita`, `regione`, `data_rilevazione`, `fonte`).
- `strings.json` + `translations/{it,en}.json` — vanno tenuti allineati a mano.

## Convenzioni

- Nessuna dipendenza esterna (`requirements: []`): HTTP solo via `async_get_clientsession`.
- Messaggi di errore e attributi in italiano; commenti/docstring in inglese.
- Errori di fetch/parsing → `UpdateFailed`, mai eccezioni grezze.
- Aggiornare `version` in `manifest.json` ad ogni release.

## Attenzione

- `_fetch_slugs()` legge gli slug dalle pagine `/province/*.html` della sitemap e li usa anche per lo scope `citta`: le città sono i 107 capoluoghi e hanno lo stesso slug (vedi https://mappacarburanti.it/llms.txt).
- I dati si aggiornano una volta al giorno (~06:00 UTC), quindi è inutile ridurre `UPDATE_INTERVAL`.
- Nuovo scope o nuovo formato API → toccare sia `_url()` sia `_normalize()` nel coordinator.

## Test

Nessun test automatico. Verifica manuale: copiare `custom_components/prezzi_carburanti/` in `config/custom_components/` di un'istanza HA, riavviare, aggiungere l'integrazione da UI e controllare le entità `sensor.*` e i log.
