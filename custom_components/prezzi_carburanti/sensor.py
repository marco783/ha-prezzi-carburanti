"""Sensor platform for Prezzi Medi Carburanti."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FUEL_TYPES, target_key, target_name
from .coordinator import PrezziCarburantiCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: PrezziCarburantiCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    async_add_entities(
        FuelPriceSensor(coordinator, entry, target_key(scope, slug), target_name(scope, slug), fuel_key)
        for scope, slug in coordinator.targets
        for fuel_key in FUEL_TYPES
        # ponytail: a location that failed the first fetch gets no sensors until the next reload
        if fuel_key in data.get(target_key(scope, slug), {}).get("fuels", {})
    )


class FuelPriceSensor(CoordinatorEntity[PrezziCarburantiCoordinator], SensorEntity):
    """Average price for one fuel type, in EUR/L, for one tracked location."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "EUR/L"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 3

    def __init__(
        self,
        coordinator: PrezziCarburantiCoordinator,
        entry: ConfigEntry,
        key: str,
        device_name: str,
        fuel_key: str,
    ) -> None:
        super().__init__(coordinator)
        name, icon = FUEL_TYPES[fuel_key]
        self._key = key
        self._fuel_key = fuel_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}_{fuel_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{key}")},
            name=device_name,
            manufacturer="mappacarburanti.it",
            model="Prezzo medio carburanti",
        )

    @property
    def _location(self) -> dict:
        return (self.coordinator.data or {}).get(self._key, {})

    @property
    def available(self) -> bool:
        return super().available and self._fuel_key in self._location.get("fuels", {})

    @property
    def native_value(self) -> float | None:
        return self._location.get("fuels", {}).get(self._fuel_key, {}).get("avg")

    @property
    def extra_state_attributes(self) -> dict:
        data = self._location
        fuel = data.get("fuels", {}).get(self._fuel_key, {})
        location = data.get("location", {})
        return {
            "min": fuel.get("min"),
            "max": fuel.get("max"),
            "stazioni_rilevate": fuel.get("count"),
            "localita": location.get("name"),
            "regione": location.get("region"),
            "data_rilevazione": data.get("date"),
            "fonte": data.get("source"),
        }
