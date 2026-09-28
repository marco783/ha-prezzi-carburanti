"""Data update coordinator for Prezzi Medi Carburanti."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CITTA_URL,
    CONF_SCOPE,
    CONF_SLUG,
    DOMAIN,
    NATIONAL_URL,
    PROVINCIA_URL,
    SCOPE_CITTA,
    SCOPE_NATIONAL,
    SCOPE_PROVINCIA,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class PrezziCarburantiCoordinator(DataUpdateCoordinator[dict]):
    """Fetches average fuel prices (national, provincia or città) once per interval."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.scope = entry.data.get(CONF_SCOPE, SCOPE_NATIONAL)
        self.slug = entry.data.get(CONF_SLUG)

    def _url(self) -> str:
        if self.scope == SCOPE_PROVINCIA:
            return PROVINCIA_URL.format(slug=self.slug)
        if self.scope == SCOPE_CITTA:
            return CITTA_URL.format(slug=self.slug)
        return NATIONAL_URL

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        url = self._url()
        try:
            async with session.get(url, timeout=15) as resp:
                resp.raise_for_status()
                payload = await resp.json(content_type=None)
        except Exception as err:  # noqa: BLE001 - surfaced as UpdateFailed
            raise UpdateFailed(f"Errore nel recupero prezzi carburanti ({url}): {err}") from err

        return self._normalize(payload)

    def _normalize(self, payload: dict) -> dict:
        """Reduce the three different API shapes to one: {fuels, date, source, location}."""
        if self.scope == SCOPE_NATIONAL:
            national = payload.get("national")
            if not national:
                raise UpdateFailed("Risposta API senza campo 'national'")
            fuels = {
                fuel: {
                    "avg": data.get("avg"),
                    "min": data.get("min"),
                    "max": data.get("max"),
                    "count": data.get("count"),
                }
                for fuel, data in national.items()
            }
            location = {"name": "Italia", "region": None}
        else:
            raw_fuels = payload.get("fuels")
            if not raw_fuels:
                raise UpdateFailed("Risposta API senza campo 'fuels'")
            fuels = {
                fuel: {
                    "avg": data.get("stats", {}).get("avg"),
                    "min": data.get("stats", {}).get("min"),
                    "max": data.get("stats", {}).get("max"),
                    "count": data.get("stats", {}).get("count"),
                }
                for fuel, data in raw_fuels.items()
            }
            if self.scope == SCOPE_PROVINCIA:
                meta = payload.get("province", {})
                location = {"name": meta.get("name"), "region": meta.get("region")}
            else:
                meta = payload.get("city", {})
                location = {"name": meta.get("name"), "region": meta.get("region")}

        return {
            "fuels": fuels,
            "date": payload.get("date"),
            "source": payload.get("source"),
            "location": location,
        }
