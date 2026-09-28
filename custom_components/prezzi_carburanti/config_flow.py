"""Config and options flow for Prezzi Medi Carburanti.

One entry tracks any mix of national average, provinces and cities, so a
household near a border between very different regional prices (e.g.
Veneto vs. Sicilia) can follow the figures that actually apply to them.
Locations are added/removed later from the entry's "Configure" button.
"""
from __future__ import annotations

import logging
import re

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_CITTA, CONF_NATIONAL, CONF_PROVINCE, DOMAIN, SITEMAP_URL

_LOGGER = logging.getLogger(__name__)


async def _fetch_slugs(hass: HomeAssistant) -> list[str]:
    # Cities are the provincial capitals and share the province slug, so the
    # /province/ pages list valid slugs for both the provincia and citta APIs.
    session = async_get_clientsession(hass)
    async with session.get(SITEMAP_URL, timeout=15) as resp:
        resp.raise_for_status()
        text = await resp.text()
    return sorted(set(re.findall(r"/province/([a-z-]+)\.html", text)))


def _schema(slugs: list[str], defaults: dict) -> vol.Schema:
    def multi() -> SelectSelector:
        return SelectSelector(
            SelectSelectorConfig(
                options=[{"value": s, "label": s.replace("-", " ").title()} for s in slugs],
                multiple=True,
                mode=SelectSelectorMode.DROPDOWN,
            )
        )

    return vol.Schema(
        {
            vol.Optional(CONF_NATIONAL, default=defaults.get(CONF_NATIONAL, True)): BooleanSelector(),
            vol.Optional(CONF_PROVINCE, default=defaults.get(CONF_PROVINCE, [])): multi(),
            vol.Optional(CONF_CITTA, default=defaults.get(CONF_CITTA, [])): multi(),
        }
    )


async def _locations_form(flow, step_id: str, user_input: dict | None, defaults: dict, done):
    """Shared by config and options flow: show the form, validate, call done(options)."""
    errors = {}
    if user_input is not None:
        if user_input.get(CONF_NATIONAL) or user_input.get(CONF_PROVINCE) or user_input.get(CONF_CITTA):
            return done(user_input)
        errors["base"] = "no_location"
        defaults = user_input

    try:
        slugs = await _fetch_slugs(flow.hass)
    except Exception as err:  # noqa: BLE001 - any network/parse failure aborts the flow
        _LOGGER.warning("Impossibile leggere l'elenco località da %s: %s", SITEMAP_URL, err)
        return flow.async_abort(reason="cannot_connect")
    if not slugs:
        return flow.async_abort(reason="cannot_connect")

    return flow.async_show_form(step_id=step_id, data_schema=_schema(slugs, defaults), errors=errors)


class PrezziCarburantiConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return await _locations_form(
            self,
            "user",
            user_input,
            {},
            lambda opts: self.async_create_entry(title="Prezzi Carburanti", data={}, options=opts),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return PrezziCarburantiOptionsFlow(config_entry)


class PrezziCarburantiOptionsFlow(OptionsFlow):
    def __init__(self, entry: ConfigEntry) -> None:
        # Not self.config_entry: assigning it is deprecated on recent HA versions
        self._entry = entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        return await _locations_form(
            self,
            "init",
            user_input,
            dict(self._entry.options),
            lambda opts: self.async_create_entry(title="", data=opts),
        )
