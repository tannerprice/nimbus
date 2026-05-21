# Nimbus

Nimbus is a custom Home Assistant integration for NOAA Weather Radio and SAME/EAS alert monitoring using RTL-SDR hardware and MQTT.

A Raspberry Pi (or other Linux host) decodes NOAA Weather Radio broadcasts and publishes normalized alert data to MQTT. Nimbus subscribes to those MQTT topics, maintains alert state/history inside Home Assistant, exposes entities, and fires Home Assistant events for automations.

Nimbus is designed around a clean separation of responsibilities:

- SDR hardware and DSP stay on the edge device
- Home Assistant handles automation, state, notifications, and UI

---

# Features

- Real-time SAME/EAS alert ingestion
- MQTT-based architecture
- Active alert tracking
- Alert expiration countdown
- Home Assistant event bus integration
- Rolling alert history
- Live NOAA audio stream URL support
- Binary sensor for active alerts
- Diagnostic entities
- Works with RTL-SDR and `rtl_fm`
- Designed for NOAA Weather Radio broadcasts

---

# Architecture

```text
RTL-SDR
   ↓
rtl_fm
   ↓
SAME Decoder
   ↓
MQTT
   ↓
Nimbus (Home Assistant)
   ↓
Entities / Automations / Notifications
```

---

# MQTT Topics

Nimbus subscribes to the following MQTT topics:

| Topic | Purpose |
|---|---|
| `nwr/alert/same` | SAME/EAS alert payloads |
| `nwr/alert/eom` | End-of-message notifications |
| `nwr/audio/url` | Live MP3 stream URL |
| `nwr/status` | Decoder runtime status |

The topic root is configurable during setup.

Default topic root:

```text
nimbus
```

---

# Example SAME Payload

```json
{
  "event_code": "TOR",
  "org": "WXR",
  "counties": ["048113"],
  "wfo": "KOUN/NWS",
  "valid_seconds": 3600,
  "issue_utc": "2026-05-20T23:12:00+00:00",
  "issue_expiry_utc": "2026-05-21T00:12:00+00:00",
  "true_remaining_secs": 2742,
  "received_utc": "2026-05-20T23:26:18+00:00",
  "raw": "ZCZC-WXR-TOR..."
}
```

---

# Home Assistant Events

Nimbus fires the following Home Assistant events:

| Event | Description |
|---|---|
| `nimbus_same_received` | Raw SAME alert received |
| `nimbus_alert_activated` | Alert became active |
| `nimbus_alert_expired` | Alert expired |
| `nimbus_eom_received` | End-of-message received |
| `nimbus_status_changed` | Decoder status changed |

---

# Entities

## Sensors

| Entity | Description |
|---|---|
| `sensor.nimbus_status` | Decoder runtime status |
| `sensor.nimbus_audio_url` | Live NOAA stream URL |
| `sensor.nimbus_last_event_code` | Last SAME event code |
| `sensor.nimbus_last_text` | Human-readable alert text |
| `sensor.nimbus_last_activation` | Last activation timestamp |
| `sensor.nimbus_expires_at` | Alert expiration timestamp |
| `sensor.nimbus_remaining_seconds` | Remaining alert duration |
| `sensor.nimbus_wfo` | Weather Forecast Office |
| `sensor.nimbus_counties` | County list |
| `sensor.nimbus_history` | History buffer size |

## Binary Sensors

| Entity | Description |
|---|---|
| `binary_sensor.nimbus_alert_active` | True when an alert is active |

---

# Installation

## HACS (Recommended)

1. Open HACS
2. Go to **Integrations**
3. Open the menu in the top-right
4. Select **Custom repositories**
5. Add your Nimbus repository URL
6. Select category: **Integration**
7. Install Nimbus
8. Restart Home Assistant

After restart:

```text
Settings → Devices & Services → Add Integration → Nimbus
```

---

## Manual Installation

Copy the integration to:

```text
/config/custom_components/nimbus/
```

Restart Home Assistant.

Then add the integration:

```text
Settings → Devices & Services → Add Integration → Nimbus
```

---

# Requirements

Nimbus requires:

- Home Assistant
- MQTT integration configured
- MQTT broker accessible from Home Assistant
- External NOAA/SAME decoder publishing MQTT messages

The SDR decoder itself runs separately from Home Assistant.

---

# Example Automation

```yaml
alias: Nimbus Alert Notification

trigger:
  - platform: event
    event_type: nimbus_alert_activated

action:
  - service: persistent_notification.create
    data:
      title: "Weather Alert"
      message: "{{ trigger.event.data.text }}"
```

---

# Example TTS Alert

```yaml
alias: Nimbus TTS Alert

trigger:
  - platform: event
    event_type: nimbus_alert_activated

action:
  - service: tts.google_translate_say
    target:
      entity_id: media_player.house_speakers
    data:
      message: "{{ trigger.event.data.text }}"
```

---

# Audio Streaming

Nimbus exposes the decoder audio stream URL as:

```text
sensor.nimbus_audio_url
```

Example value:

```text
http://192.168.1.10:8765/nwr.mp3
```

This can be used in dashboards, media players, or automations.

---

# Alert History

Nimbus maintains a rolling in-memory alert history buffer.

Default size:

```text
50 alerts
```

This is configurable during setup.

History is exposed via attributes on:

```text
sensor.nimbus_history
```

---

# Design Philosophy

Nimbus intentionally keeps SDR decoding separate from Home Assistant.

The decoder device should only:

- receive RF
- decode SAME/EAS
- normalize payloads
- publish MQTT

Nimbus handles:

- Home Assistant state
- entities
- automations
- notifications
- event dispatching
- dashboards
- history
- alert lifecycle management

---

# Future Plans

- CAP/IPAWS support
- Tornado polygon mapping
- Weather radar overlays
- Custom Lovelace cards
- Severity classification
- Media player integration
- Recorder-backed persistent history
- Multi-radio support
- County filtering inside Home Assistant
- Rich push notifications
- Alert deduplication and correlation

---

# Repository Layout

```text
repository-root/
├── README.md
├── LICENSE
├── hacs.json
├── custom_components/
│   └── nimbus/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── sensor.py
│       ├── binary_sensor.py
│       └── diagnostics.py
```

---

# License

MIT License

---

# Disclaimer

Nimbus is not affiliated with NOAA, NWS, FEMA, IPAWS, or the Emergency Alert System.

Always rely on official emergency alerting systems for life safety information.
