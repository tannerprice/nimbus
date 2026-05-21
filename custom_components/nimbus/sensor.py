from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NimbusCoordinator
from .const import DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True, kw_only=True)
class NimbusSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Any], Any] | None = None
    attr_fn: Callable[[Any], dict[str, Any]] | None = None


def _last_alert_attr(coordinator) -> dict[str, Any]:
    alert = coordinator.data.last_alert or {}

    return {
        "raw": alert.get("raw"),
        "org": alert.get("org"),
        "wfo": alert.get("wfo"),
        "counties": alert.get("counties"),
        "issue_utc": alert.get("issue_utc"),
        "issue_expiry_utc": alert.get("issue_expiry_utc"),
        "received_utc": alert.get("received_utc"),
        "valid_seconds": alert.get("valid_seconds"),
    }


def _history_attr(coordinator) -> dict[str, Any]:
    return {
        "history": coordinator.history_as_list(),
    }


SENSORS: tuple[NimbusSensorDescription, ...] = (
    NimbusSensorDescription(
        key="status",
        name="Nimbus Status",
        value_fn=lambda c: c.data.status,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NimbusSensorDescription(
        key="audio_url",
        name="Nimbus Audio URL",
        value_fn=lambda c: c.data.audio_url,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NimbusSensorDescription(
        key="last_event_code",
        name="Nimbus Last Event Code",
        value_fn=lambda c: c.data.last_event_code,
        attr_fn=_last_alert_attr,
    ),
    NimbusSensorDescription(
        key="last_text",
        name="Nimbus Last Text",
        value_fn=lambda c: c.data.last_text,
    ),
    NimbusSensorDescription(
        key="last_activation",
        name="Nimbus Last Activation",
        value_fn=lambda c: c.data.last_activation,
    ),
    NimbusSensorDescription(
        key="expires_at",
        name="Nimbus Expires At",
        value_fn=lambda c: c.data.expires_at,
    ),
    NimbusSensorDescription(
        key="remaining_seconds",
        name="Nimbus Remaining Seconds",
        native_unit_of_measurement="s",
        value_fn=lambda c: c.remaining_seconds(),
    ),
    NimbusSensorDescription(
        key="wfo",
        name="Nimbus WFO",
        value_fn=lambda c: (c.data.last_alert or {}).get("wfo"),
    ),
    NimbusSensorDescription(
        key="counties",
        name="Nimbus Counties",
        value_fn=lambda c: (
            ", ".join((c.data.last_alert or {}).get("counties", []))
            if c.data.last_alert
            else None
        ),
    ),
    NimbusSensorDescription(
        key="history",
        name="Nimbus History",
        value_fn=lambda c: len(c.history_as_list()),
        attr_fn=_history_attr,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    async_add_entities(
        NimbusSensor(coordinator, entry, description) for description in SENSORS
    )


class NimbusSensor(CoordinatorEntity[NimbusCoordinator], SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    def __init__(
        self,
        coordinator: NimbusCoordinator,
        entry: ConfigEntry,
        description: NimbusSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._update_attrs()

    def _update_attrs(self) -> None:
        description = cast(NimbusSensorDescription, self.entity_description)

        if description.value_fn is None:
            self._attr_native_value = None
        else:
            self._attr_native_value = description.value_fn(self.coordinator)

        if description.attr_fn is None:
            self._attr_extra_state_attributes = {}
        else:
            self._attr_extra_state_attributes = description.attr_fn(self.coordinator)

    def _handle_coordinator_update(self) -> None:
        self._update_attrs()
        self.async_write_ha_state()
