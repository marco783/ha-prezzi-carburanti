"""The Prezzi Medi Carburanti integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_CITTA,
    CONF_NATIONAL,
    CONF_PROVINCE,
    CONF_SCOPE,
    CONF_SLUG,
    DOMAIN,
    SCOPE_CITTA,
    SCOPE_NATIONAL,
    SCOPE_PROVINCIA,
    target_key,
)
from .coordinator import PrezziCarburantiCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = PrezziCarburantiCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Drop devices (and their entities) of locations removed in the options
    wanted = {(DOMAIN, f"{entry.entry_id}_{target_key(s, g)}") for s, g in coordinator.targets}
    dev_reg = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        if not device.identifiers & wanted:
            dev_reg.async_update_device(device.id, remove_config_entry_id=entry.entry_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """v1 (one scope/slug per entry, in data) -> v2 (locations list, in options).

    Keeps entity_ids and history by rewriting unique_ids and the device identifier.
    """
    if entry.version == 1:
        scope = entry.data.get(CONF_SCOPE, SCOPE_NATIONAL)
        slug = entry.data.get(CONF_SLUG)
        key = target_key(scope, slug)

        @callback
        def _new_uid(ent: er.RegistryEntry) -> dict | None:
            fuel = ent.unique_id.removeprefix(f"{entry.entry_id}_")
            return {"new_unique_id": f"{entry.entry_id}_{key}_{fuel}"}

        await er.async_migrate_entries(hass, entry.entry_id, _new_uid)

        dev_reg = dr.async_get(hass)
        if device := dev_reg.async_get_device(identifiers={(DOMAIN, entry.entry_id)}):
            dev_reg.async_update_device(
                device.id, new_identifiers={(DOMAIN, f"{entry.entry_id}_{key}")}
            )

        options = {
            CONF_NATIONAL: scope == SCOPE_NATIONAL,
            CONF_PROVINCE: [slug] if scope == SCOPE_PROVINCIA else [],
            CONF_CITTA: [slug] if scope == SCOPE_CITTA else [],
        }
        hass.config_entries.async_update_entry(
            entry, title="Prezzi Carburanti", data={}, options=options, version=2
        )
    return True
