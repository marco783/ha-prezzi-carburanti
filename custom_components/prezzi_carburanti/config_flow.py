"""Config flow for Prezzi Medi Carburanti.

Lets the user pick a scope (national average, or a province/city average)
so a household near a border between very different regional prices (e.g.
Veneto vs. Sicilia) can track the figure that actually applies to them,
instead of only the national blend.
"""
from __future__ import annotations

import logging
import re

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import (
    CONF_SCOPE,
    CONF_SLUG,
    DOMAIN,
    SCOPE_CITTA,
    SCOPE_NATIONAL,
    SCOPE_PROVINCIA,
    SITEMAP_URL,
)

_LOGGER = logging.getLogger(__name__)

SCOPE_LABELS = {
    SCOPE_NATIONAL: "Media nazionale",
    SCOPE_PROVINCIA: "Provincia",
    SCOPE_CITTA: "Città",
}


class PrezziCarburantiConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._scope: str | None = None

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            self._scope = user_input[CONF_SCOPE]
            if self._scope == SCOPE_NATIONAL:
                return await self._finish(SCOPE_NATIONAL, None)
            return await self.async_step_location()

        schema = vol.Schema(
            {
                vol.Required(CONF_SCOPE, default=SCOPE_NATIONAL): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": key, "label": label}
                            for key, label in SCOPE_LABELS.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_location(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return await self._finish(self._scope, user_input[CONF_SLUG])

        try:
            slugs = await self._fetch_slugs()
        except Exception as err:  # noqa: BLE001 - any network/parse failure aborts the flow
            _LOGGER.warning("Impossibile leggere l'elenco località da %s: %s", SITEMAP_URL, err)
            return self.async_abort(reason="cannot_connect")
        if not slugs:
            return self.async_abort(reason="cannot_connect")

        schema = vol.Schema(
            {
                vol.Required(CONF_SLUG): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": slug, "label": slug.replace("-", " ").title()}
                            for slug in slugs
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="location", data_schema=schema)

    async def _fetch_slugs(self) -> list[str]:
        # Cities are the provincial capitals and share the province slug, so the
        # /province/ pages list valid slugs for both the provincia and citta APIs.
        session = async_get_clientsession(self.hass)
        async with session.get(SITEMAP_URL, timeout=15) as resp:
            resp.raise_for_status()
            text = await resp.text()
        return sorted(set(re.findall(r"/province/([a-z-]+)\.html", text)))

    async def _finish(self, scope: str, slug: str | None) -> FlowResult:
        unique_id = f"{scope}:{slug}" if slug else scope
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        title = SCOPE_LABELS[scope]
        if slug:
            title = f"{title} — {slug.replace('-', ' ').title()}"

        data = {CONF_SCOPE: scope}
        if slug:
            data[CONF_SLUG] = slug
        return self.async_create_entry(title=title, data=data)
