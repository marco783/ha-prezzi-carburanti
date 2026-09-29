"""Constants for the Prezzi Medi Carburanti integration."""
from datetime import timedelta

DOMAIN = "prezzi_carburanti"
UPDATE_INTERVAL = timedelta(hours=6)

PRICES_URL = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
STATIONS_URL = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
STATIONS_TTL = timedelta(hours=24)

SCOPE_NATIONAL = "national"
SCOPE_PROVINCIA = "provincia"
SCOPE_CITTA = "citta"

SCOPE_LABELS = {
    SCOPE_NATIONAL: "Media nazionale",
    SCOPE_PROVINCIA: "Provincia",
    SCOPE_CITTA: "Città",
}

# Options (entry.options): what the single entry tracks
CONF_NATIONAL = "national"
CONF_PROVINCE = "province"
CONF_CITTA = "citta"

# Legacy v1 entry.data keys, read only by the migration
CONF_SCOPE = "scope"
CONF_SLUG = "slug"

# key -> (friendly name, icon)
FUEL_TYPES = {
    "benzina": ("Benzina", "mdi:gas-station"),
    "gasolio": ("Gasolio", "mdi:gas-station"),
    "gpl": ("GPL", "mdi:gas-station-outline"),
    "metano": ("Metano", "mdi:gas-cylinder"),
}


def target_key(scope: str, slug: str | None) -> str:
    """Stable id of one tracked location, used in unique_ids and device identifiers."""
    return scope if scope == SCOPE_NATIONAL else f"{scope}_{slug}"


def target_name(scope: str, slug: str | None) -> str:
    """Device name, e.g. 'Provincia — Verona' (drives the entity_id)."""
    if scope == SCOPE_NATIONAL:
        return SCOPE_LABELS[scope]
    return f"{SCOPE_LABELS[scope]} — {slug.replace('-', ' ').title()}"


def targets_from_options(options: dict) -> list[tuple[str, str | None]]:
    """(scope, slug) pairs selected in the entry options."""
    targets: list[tuple[str, str | None]] = []
    if options.get(CONF_NATIONAL):
        targets.append((SCOPE_NATIONAL, None))
    targets += [(SCOPE_PROVINCIA, s) for s in options.get(CONF_PROVINCE, [])]
    targets += [(SCOPE_CITTA, s) for s in options.get(CONF_CITTA, [])]
    return targets
