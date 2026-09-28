# Prezzi Medi Carburanti

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![GitHub release](https://img.shields.io/github/v/release/marco783/ha-prezzi-carburanti)](https://github.com/marco783/ha-prezzi-carburanti/releases)

Integrazione per [Home Assistant](https://www.home-assistant.io/) che espone il **prezzo medio di benzina, gasolio, GPL e metano** in Italia, letto da [mappacarburanti.it](https://mappacarburanti.it) (dati ufficiali MIMIT, licenza CC0-1.0).

Puoi seguire la media nazionale oppure quella di una provincia o di una città: i prezzi variano molto da regione a regione.

## Funzionalità

- Tre ambiti: **nazionale**, **provincia** (~28 km dal capoluogo), **città** (~7 km dal centro), per i 107 capoluoghi
- Un sensore per ogni carburante disponibile, in EUR/L
- Minimo, massimo e numero di stazioni come attributi
- Più località nella stessa integrazione, per confrontare zone diverse
- Località aggiunte o rimosse in qualsiasi momento da **Configura**
- Configurazione interamente da UI, senza API key
- Aggiornamento ogni 6 ore (la fonte pubblica dati nuovi una volta al giorno)

## Installazione

### HACS (consigliata)

1. HACS → menu ⋮ → **Repository personalizzati**
2. Aggiungi `https://github.com/marco783/ha-prezzi-carburanti`, categoria **Integrazione**
3. Cerca **Prezzi Medi Carburanti** → **Scarica**
4. Riavvia Home Assistant

### Manuale

Copia la cartella `custom_components/prezzi_carburanti/` di questo repository in `config/custom_components/` e riavvia Home Assistant.

## Configurazione

1. **Impostazioni → Dispositivi e servizi → Aggiungi integrazione**
2. Cerca **Prezzi Medi Carburanti**
3. Scegli cosa seguire, anche più cose insieme:
   - **Media nazionale** (interruttore)
   - **Province**: una o più, dal menu a selezione multipla
   - **Città**: una o più, dal menu a selezione multipla

Per aggiungere o togliere località in seguito: **Impostazioni → Dispositivi e servizi → Prezzi Medi Carburanti → Configura**. I sensori delle località rimosse vengono eliminati automaticamente.

## Sensori

Ogni località selezionata crea un dispositivo con un sensore per carburante:

| Sensore   | Esempio entity_id                    | Unità |
|-----------|--------------------------------------|-------|
| Benzina   | `sensor.media_nazionale_benzina`     | EUR/L |
| Gasolio   | `sensor.media_nazionale_gasolio`     | EUR/L |
| GPL       | `sensor.media_nazionale_gpl`         | EUR/L |
| Metano    | `sensor.media_nazionale_metano`      | EUR/L |

L'`entity_id` dipende dalla località:

| Località           | Esempio entity_id                  |
|--------------------|------------------------------------|
| Media nazionale    | `sensor.media_nazionale_gasolio`   |
| Provincia di Verona| `sensor.provincia_verona_gasolio`  |
| Città di Verona    | `sensor.citta_verona_gasolio`      |

### Attributi

| Attributo           | Descrizione                                  |
|---------------------|----------------------------------------------|
| `min`               | Prezzo minimo rilevato                       |
| `max`               | Prezzo massimo rilevato                      |
| `stazioni_rilevate` | Numero di distributori inclusi nella media   |
| `localita`          | Nome della località                          |
| `regione`           | Regione (per provincia e città)              |
| `data_rilevazione`  | Data dei dati                                |
| `fonte`             | Fonte dei dati                               |

## Esempio: notifica quando la benzina scende

```yaml
automation:
  - alias: Benzina sotto 1,80 €/L
    triggers:
      - trigger: numeric_state
        entity_id: sensor.media_nazionale_benzina
        below: 1.80
    actions:
      - action: notify.notify
        data:
          message: "Benzina a {{ states('sensor.media_nazionale_benzina') }} €/L"
```

## Fonte dati

- `https://mappacarburanti.it/api/prezzi/national.json`
- `https://mappacarburanti.it/api/prezzi/provincia/{slug}.json`
- `https://mappacarburanti.it/api/prezzi/citta/{slug}.json`

L'elenco delle località viene letto dalla sitemap del sito durante la configurazione. Non serve autenticazione.

Questa integrazione non è affiliata a mappacarburanti.it né al MIMIT.

## Problemi e suggerimenti

Apri una [issue](https://github.com/marco783/ha-prezzi-carburanti/issues).

---

> ℹ️ Questa integrazione è stata sviluppata con l'ausilio dell'intelligenza artificiale ([Claude Code](https://claude.com/claude-code)). Se trovi comportamenti anomali [segnalali](https://github.com/marco783/ha-prezzi-carburanti/issues).
