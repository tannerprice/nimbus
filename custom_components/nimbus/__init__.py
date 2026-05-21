from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.components.mqtt.client import async_subscribe
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .alerts import ALERTS
from .const import (
    CONF_HISTORY_LIMIT,
    CONF_TOPIC_ROOT,
    DATA_COORDINATOR,
    DATA_UNSUB_MQTT,
    DATA_UNSUB_TIMER,
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_TOPIC_ROOT,
    DOMAIN,
    EVENT_ALERT_ACTIVATED,
    EVENT_ALERT_EXPIRED,
    EVENT_EOM_RECEIVED,
    EVENT_SAME_RECEIVED,
    EVENT_STATUS_CHANGED,
    TOPIC_ALERT_EOM,
    TOPIC_ALERT_SAME,
    TOPIC_AUDIO_URL,
    TOPIC_STATUS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


@dataclass
class NimbusRuntimeState:
    status: str | None = None
    audio_url: str | None = None

    active_alert: dict[str, Any] | None = None
    last_alert: dict[str, Any] | None = None
    last_eom: dict[str, Any] | None = None

    last_activation: str | None = None
    expires_at: str | None = None
    last_text: str | None = None
    last_event_code: str | None = None

    alert_active: bool = False
    expired_event_fired: bool = False

    tracked_alerts: dict[str, dict[str, Any]] = field(default_factory=dict)
    history: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=50))


class NimbusCoordinator(DataUpdateCoordinator[NimbusRuntimeState]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        topic_root: str,
        history_limit: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self.entry = entry
        self.topic_root = topic_root.strip().strip("/")
        self.data = NimbusRuntimeState(history=deque(maxlen=history_limit))

    async def _async_update_data(self) -> NimbusRuntimeState:
        self._update_expiry_state()
        return self.data

    def remaining_seconds_for(self, expires_at: str | None) -> int | None:
        if not expires_at:
            return None

        expires = dt_util.parse_datetime(expires_at)
        if expires is None:
            return None

        if expires.tzinfo is None:
            expires = dt_util.as_utc(expires)

        return max(0, int((expires - dt_util.utcnow()).total_seconds()))

    def _is_expired(self, expires_at: str | None) -> bool:
        remaining = self.remaining_seconds_for(expires_at)
        return remaining is not None and remaining <= 0

    @callback
    def handle_status(self, payload: str) -> None:
        previous_status = self.data.status
        self.data.status = payload.strip() if payload else None

        if previous_status != self.data.status:
            self.hass.bus.async_fire(
                EVENT_STATUS_CHANGED,
                {
                    "status": self.data.status,
                    "previous_status": previous_status,
                    "config_entry_id": self.entry.entry_id,
                },
            )

        self.async_set_updated_data(self.data)

    @callback
    def handle_audio_url(self, payload: str) -> None:
        self.data.audio_url = payload.strip() if payload else None
        self.async_set_updated_data(self.data)

    @callback
    def handle_same(self, payload: str) -> None:
        try:
            alert = json.loads(payload)
        except json.JSONDecodeError:
            _LOGGER.warning("Invalid SAME JSON payload: %s", payload)
            return

        now = dt_util.utcnow().isoformat()
        alert.setdefault("received_homeassistant_utc", now)

        event_code = alert.get("event_code")
        expires_at = alert.get("issue_expiry_utc")
        received_at = alert.get("received_utc") or now
        text = self._build_alert_text(alert)

        definition = ALERTS.get(event_code)

        if definition:
            self.data.tracked_alerts[event_code] = {
                "active": True,
                "event_code": event_code,
                "name": definition.name,
                "category": definition.category,
                "severity": definition.severity,
                "icon": definition.icon,
                "color": definition.color,
                "counties": alert.get("counties", []),
                "wfo": alert.get("wfo"),
                "expires_at": expires_at,
                "received_utc": received_at,
                "text": text,
                "raw": alert.get("raw"),
                "payload": alert,
            }

        self.data.last_alert = alert
        self.data.active_alert = alert
        self.data.last_activation = received_at
        self.data.expires_at = expires_at
        self.data.last_text = text
        self.data.last_event_code = event_code
        self.data.alert_active = True
        self.data.expired_event_fired = False

        self.data.history.appendleft(
            {
                "type": "same",
                "event_code": event_code,
                "text": text,
                "received_utc": received_at,
                "expires_at": expires_at,
                "payload": alert,
            }
        )

        event_payload = {
            **alert,
            "text": text,
            "config_entry_id": self.entry.entry_id,
        }

        self.hass.bus.async_fire(EVENT_SAME_RECEIVED, event_payload)
        self.hass.bus.async_fire(EVENT_ALERT_ACTIVATED, event_payload)

        self.async_set_updated_data(self.data)

    @callback
    def handle_eom(self, payload: str) -> None:
        try:
            eom = json.loads(payload)
        except json.JSONDecodeError:
            eom = {"raw": payload}

        eom.setdefault("received_homeassistant_utc", dt_util.utcnow().isoformat())

        previous_alert = self.data.active_alert

        self.data.last_eom = eom
        self.data.alert_active = False
        self.data.active_alert = None
        self.data.expired_event_fired = True

        self.data.history.appendleft(
            {
                "type": "eom",
                "received_utc": eom.get("eom_utc") or eom["received_homeassistant_utc"],
                "payload": eom,
            }
        )

        self.hass.bus.async_fire(
            EVENT_EOM_RECEIVED,
            {
                **eom,
                "previous_alert": previous_alert,
                "config_entry_id": self.entry.entry_id,
            },
        )

        self.async_set_updated_data(self.data)

    @callback
    def tick(self, now=None) -> None:
        changed = self._update_expiry_state()

        if changed:
            self.async_set_updated_data(self.data)
        else:
            self.async_update_listeners()

    @callback
    def _update_expiry_state(self) -> bool:
        changed = False

        if self.data.alert_active and self.data.expires_at:
            if self._is_expired(self.data.expires_at):
                self.data.alert_active = False
                self.data.active_alert = None
                changed = True

                if not self.data.expired_event_fired:
                    self.data.expired_event_fired = True
                    self.hass.bus.async_fire(
                        EVENT_ALERT_EXPIRED,
                        {
                            "last_alert": self.data.last_alert,
                            "expires_at": self.data.expires_at,
                            "config_entry_id": self.entry.entry_id,
                        },
                    )

        for code, alert in self.data.tracked_alerts.items():
            if alert.get("active") and self._is_expired(alert.get("expires_at")):
                alert["active"] = False
                changed = True

        return changed

    def remaining_seconds(self) -> int | None:
        if not self.data.expires_at:
            return None

        expires = dt_util.parse_datetime(self.data.expires_at)
        if expires is None:
            return None

        if expires.tzinfo is None:
            expires = dt_util.as_utc(expires)

        return max(0, int((expires - dt_util.utcnow()).total_seconds()))

    def history_as_list(self) -> list[dict[str, Any]]:
        return list(self.data.history)

    def _build_alert_text(self, alert: dict[str, Any]) -> str:
        event_code = alert.get("event_code") or "Unknown"
        definition = ALERTS.get(event_code)

        event_name = definition.name if definition else event_code
        counties = alert.get("counties") or []
        wfo = alert.get("wfo") or "Unknown WFO"
        remaining = alert.get("true_remaining_secs")

        counties_text = (
            ", ".join(str(c) for c in counties)
            if isinstance(counties, list)
            else str(counties)
        )

        if remaining is not None:
            return f"{event_name} from {wfo} for {counties_text}. {remaining} seconds remaining."

        return f"{event_name} from {wfo} for {counties_text}."


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    topic_root = entry.data.get(CONF_TOPIC_ROOT, DEFAULT_TOPIC_ROOT)
    history_limit = entry.data.get(CONF_HISTORY_LIMIT, DEFAULT_HISTORY_LIMIT)

    coordinator = NimbusCoordinator(
        hass=hass,
        entry=entry,
        topic_root=topic_root,
        history_limit=history_limit,
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_UNSUB_MQTT: [],
        DATA_UNSUB_TIMER: None,
    }

    async def subscribe(relative_topic: str, handler):
        topic = f"{topic_root}/{relative_topic}"

        @callback
        def message_received(msg):
            handler(msg.payload)

        unsub = await async_subscribe(
            hass,
            topic,
            message_received,
            qos=0,
            encoding="utf-8",
        )

        hass.data[DOMAIN][entry.entry_id][DATA_UNSUB_MQTT].append(unsub)
        _LOGGER.info("Nimbus subscribed to MQTT topic %s", topic)

    await subscribe(TOPIC_ALERT_SAME, coordinator.handle_same)
    await subscribe(TOPIC_ALERT_EOM, coordinator.handle_eom)
    await subscribe(TOPIC_AUDIO_URL, coordinator.handle_audio_url)
    await subscribe(TOPIC_STATUS, coordinator.handle_status)

    hass.data[DOMAIN][entry.entry_id][DATA_UNSUB_TIMER] = async_track_time_interval(
        hass,
        coordinator.tick,
        timedelta(seconds=15),
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    data = hass.data[DOMAIN].pop(entry.entry_id)

    for unsub in data.get(DATA_UNSUB_MQTT, []):
        unsub()

    if data.get(DATA_UNSUB_TIMER):
        data[DATA_UNSUB_TIMER]()

    return unload_ok
