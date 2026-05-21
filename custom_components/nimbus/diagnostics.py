from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DATA_COORDINATOR, DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    return {
        "topic_root": coordinator.topic_root,
        "status": coordinator.data.status,
        "audio_url": coordinator.data.audio_url,
        "last_alert": coordinator.data.last_alert,
        "last_eom": coordinator.data.last_eom,
        "history_count": len(coordinator.history_as_list()),
    }
