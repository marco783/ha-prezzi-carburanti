# CLAUDE.md

Custom integration Home Assistant `prezzi_carburanti`: prezzi medi dei carburanti (benzina, gasolio, GPL, metano) da mappacarburanti.it, a livello nazionale, di provincia o di città. Distribuita via HACS.

## Struttura

Layout HACS standard: `hacs.json`, `README.md` e questo file alla root; il codice in `custom_components/prezzi_carburanti/` (percorsi sotto relativi a quella cartella).

- `const.py` — dominio, URL API, scope (`national` / `provincia` / `citta`), `FUEL_TYPES`, helper `target_key` / `target_name` / `targets_from_options`.
- `config_flow.py` — **una sola entry** (VERSION 2). Stesso form (`_locations_form`) per config flow e options flow («Configura»): interruttore nazionale + multi-select province + multi-select città. La selezione vive in `entry.options` (`national`, `province`, `citta`); `entry.data` è vuoto.
- `__init__.py` — setup, reload quando cambiano le options, rimozione dei device delle località tolte, `async_migrate_entry` v1→v2 (una entry per scope/slug in `data` → options; riscrive unique_id e identifier del device per non perdere entity_id e storico).
- `coordinator.py` — `DataUpdateCoordinator`, polling ogni 6h, fetch in parallelo di tutte le località. `data = {target_key: {fuels, date, source, location}}`, con `fuels = {fuel: {avg, min, max, count}}`. Una località che fallisce manca da `data` (solo i suoi sensori diventano unavailable); se falliscono tutte → `UpdateFailed`.
- `sensor.py` — un device per località (nome da `target_name`, es. «Provincia — Verona»), un `FuelPriceSensor` per carburante; unique_id `{entry_id}_{target_key}_{fuel}`; stato = `avg` in EUR/L, attributi in italiano (`min`, `max`, `stazioni_rilevate`, `localita`, `regione`, `data_rilevazione`, `fonte`).
- `strings.json` + `translations/{it,en}.json` — vanno tenuti allineati a mano.

## Convenzioni

- Nessuna dipendenza esterna (`requirements: []`): HTTP solo via `async_get_clientsession`.
- Messaggi di errore e attributi in italiano; commenti/docstring in inglese.
- Errori di fetch/parsing: `_fetch`/`_normalize` sollevano, `_async_update_data` li raccoglie per località.
- Aggiornare `version` in `manifest.json` ad ogni release.

## Attenzione

- `_fetch_slugs()` legge gli slug dalle pagine `/province/*.html` della sitemap e li usa anche per lo scope `citta`: le città sono i 107 capoluoghi e hanno lo stesso slug (vedi https://mappacarburanti.it/llms.txt).
- I dati si aggiornano una volta al giorno (~06:00 UTC), quindi è inutile ridurre `UPDATE_INTERVAL`.
- `national.json` ha le statistiche per carburante piatte; `provincia`/`citta` le annidano in `stats`. `_normalize` gestisce entrambe.
- Cambiare `target_key` o il formato degli unique_id rompe entity_id e storico degli utenti: serve una migrazione.

## Test

`python tests/test_logic.py`: self-check della logica pura (normalizzazione API, options → località) con HA stubbato; gira con Python liscio.

Verifica manuale in HA: copiare `custom_components/prezzi_carburanti/` in `config/custom_components/` di un'istanza HA, riavviare, aggiungere l'integrazione da UI e controllare le entità `sensor.*` e i log.
