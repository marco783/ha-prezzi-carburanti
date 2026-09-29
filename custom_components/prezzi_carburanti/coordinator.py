"""Data update coordinator for Prezzi Medi Carburanti."""
from __future__ import annotations

import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, PRICES_URL, STATIONS_TTL, STATIONS_URL, UPDATE_INTERVAL, targets_from_options
from .mimit import compute, decode

_LOGGER = logging.getLogger(__name__)


class PrezziCarburantiCoordinator(DataUpdateCoordinator[dict]):
    """Downloads the MIMIT CSVs and averages prices for every location in the entry options.

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
        self._stations: bytes | None = None
        self._stations_at = None

    async def _get(self, url: str) -> bytes:
        session = async_get_clientsession(self.hass)
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def _async_update_data(self) -> dict:
        try:
            prices = await self._get(PRICES_URL)
            if self._stations is None or dt_util.utcnow() - self._stations_at > STATIONS_TTL:
                self._stations = await self._get(STATIONS_URL)
                self._stations_at = dt_util.utcnow()
            data = await self.hass.async_add_executor_job(
                compute, decode(prices), decode(self._stations), self.targets
            )
        except Exception as err:  # noqa: BLE001 - network or parse error: keep last data
            raise UpdateFailed(f"MIMIT: {err}") from err
        if not data:
            raise UpdateFailed("Nessuna località con prezzi validi")
        return data
