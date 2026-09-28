"""Data update coordinator for Prezzi Medi Carburanti."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CITTA_URL,
    DOMAIN,
    NATIONAL_URL,
    PROVINCIA_URL,
    SCOPE_CITTA,
    SCOPE_NATIONAL,
    SCOPE_PROVINCIA,
    UPDATE_INTERVAL,
    target_key,
    targets_from_options,
)

_LOGGER = logging.getLogger(__name__)


class PrezziCarburantiCoordinator(DataUpdateCoordinator[dict]):
    """Fetches average fuel prices for every location selected in the entry options.

    data = {target_key: {fuels, date, source, location}}; a location whose fetch
    failed is simply missing, so only its sensors go unavailable.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.targets = targets_from_options(entry.options)

    async def _async_update_data(self) -> dict:
        results = await asyncio.gather(
            *(self._fetch(scope, slug) for scope, slug in self.targets),
            return_exceptions=True,
        )
        data = {}
        for (scope, slug), result in zip(self.targets, results):
            if isinstance(result, Exception):
                _LOGGER.warning("Prezzi non disponibili per %s: %s", target_key(scope, slug), result)
            else:
                data[target_key(scope, slug)] = result
        if not data:
            raise UpdateFailed("Nessuna località aggiornata, vedi i log")
        return data

    async def _fetch(self, scope: str, slug: str | None) -> dict:
        if scope == SCOPE_PROVINCIA:
            url = PROVINCIA_URL.format(slug=slug)
        elif scope == SCOPE_CITTA:
            url = CITTA_URL.format(slug=slug)
        else:
            url = NATIONAL_URL
        session = async_get_clientsession(self.hass)
        async with session.get(url, timeout=15) as resp:
            resp.raise_for_status()
            payload = await resp.json(content_type=None)
        return _normalize(scope, payload)


def _normalize(scope: str, payload: dict) -> dict:
    """Reduce the API shapes to one: {fuels, date, source, location}.

    national.json has flat per-fuel stats; provincia/citta nest them under "stats".
    """
    raw_fuels = payload.get("fuels")
    if not raw_fuels:
        raise ValueError("risposta API senza campo 'fuels'")
    fuels = {
        fuel: {k: data.get("stats", data).get(k) for k in ("avg", "min", "max", "count")}
        for fuel, data in raw_fuels.items()
    }
    if scope == SCOPE_NATIONAL:
        location = {"name": "Italia", "region": None}
    else:
        meta = payload.get("province" if scope == SCOPE_PROVINCIA else "city", {})
        location = {"name": meta.get("name"), "region": meta.get("region")}

    return {
        "fuels": fuels,
        "date": payload.get("date"),
        "source": payload.get("source"),
        "location": location,
    }
