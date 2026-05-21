from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NimbusCoordinator
from .const import DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True, kw_only=True)
class NimbusBinarySensorDescription(BinarySensorEntityDescription):
    pass


BINARY_SENSORS: tuple[NimbusBinarySensorDescription, ...] = (
    NimbusBinarySensorDescription(
        key="alert_active",
        name="Nimbus Alert Active",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    async_add_entities(
        NimbusBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSORS
    )


class NimbusBinarySensor(CoordinatorEntity[NimbusCoordinator], BinarySensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    def __init__(
        self,
        coordinator: NimbusCoordinator,
        entry: ConfigEntry,
        description: NimbusBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._update_attrs()

    def _update_attrs(self) -> None:
        alert = self.coordinator.data.last_alert or {}

        self._attr_is_on = bool(self.coordinator.data.alert_active)
        self._attr_extra_state_attributes = {
            "event_code": alert.get("event_code"),
            "text": self.coordinator.data.last_text,
            "expires_at": self.coordinator.data.expires_at,
            "remaining_seconds": self.coordinator.remaining_seconds(),
            "wfo": alert.get("wfo"),
            "counties": alert.get("counties"),
            "raw": alert.get("raw"),
        }

    def _handle_coordinator_update(self) -> None:
        self._update_attrs()
        self.async_write_ha_state()
