"""Constants for the Prezzi Medi Carburanti integration."""
from datetime import timedelta

DOMAIN = "prezzi_carburanti"
UPDATE_INTERVAL = timedelta(hours=6)

SITEMAP_URL = "https://mappacarburanti.it/sitemap.xml"
NATIONAL_URL = "https://mappacarburanti.it/api/prezzi/national.json"
PROVINCIA_URL = "https://mappacarburanti.it/api/prezzi/provincia/{slug}.json"
CITTA_URL = "https://mappacarburanti.it/api/prezzi/citta/{slug}.json"

SCOPE_NATIONAL = "national"
SCOPE_PROVINCIA = "provincia"
SCOPE_CITTA = "citta"
SCOPES = [SCOPE_NATIONAL, SCOPE_PROVINCIA, SCOPE_CITTA]

CONF_SCOPE = "scope"
CONF_SLUG = "slug"

# key -> (friendly name, icon)
FUEL_TYPES = {
    "benzina": ("Benzina", "mdi:gas-station"),
    "gasolio": ("Gasolio", "mdi:gas-station"),
    "gpl": ("GPL", "mdi:gas-station-outline"),
    "metano": ("Metano", "mdi:gas-cylinder"),
}
