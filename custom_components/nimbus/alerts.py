from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertDefinition:
    code: str
    name: str
    category: str
    severity: str
    icon: str
    color: str


ALERTS: dict[str, AlertDefinition] = {
    "BZW": AlertDefinition(
        "BZW", "Blizzard Warning", "weather", "high", "mdi:snowflake-alert", "#60a5fa"
    ),
    "CFA": AlertDefinition(
        "CFA", "Coastal Flood Watch", "weather", "moderate", "mdi:waves", "#38bdf8"
    ),
    "CFW": AlertDefinition(
        "CFW",
        "Coastal Flood Warning",
        "weather",
        "high",
        "mdi:waves-arrow-up",
        "#0284c7",
    ),
    "DSW": AlertDefinition(
        "DSW", "Dust Storm Warning", "weather", "high", "mdi:weather-dust", "#a16207"
    ),
    "EWW": AlertDefinition(
        "EWW",
        "Extreme Wind Warning",
        "weather",
        "extreme",
        "mdi:weather-windy",
        "#dc2626",
    ),
    "FFA": AlertDefinition(
        "FFA", "Flash Flood Watch", "weather", "moderate", "mdi:waves", "#3b82f6"
    ),
    "FFW": AlertDefinition(
        "FFW", "Flash Flood Warning", "weather", "high", "mdi:waves-arrow-up", "#2563eb"
    ),
    "FFS": AlertDefinition(
        "FFS",
        "Flash Flood Statement",
        "weather",
        "statement",
        "mdi:message-alert",
        "#64748b",
    ),
    "FLA": AlertDefinition(
        "FLA", "Flood Watch", "weather", "moderate", "mdi:home-flood", "#38bdf8"
    ),
    "FLW": AlertDefinition(
        "FLW", "Flood Warning", "weather", "high", "mdi:home-flood", "#0284c7"
    ),
    "FLS": AlertDefinition(
        "FLS", "Flood Statement", "weather", "statement", "mdi:message-alert", "#64748b"
    ),
    "HWA": AlertDefinition(
        "HWA", "High Wind Watch", "weather", "moderate", "mdi:weather-windy", "#f59e0b"
    ),
    "HWW": AlertDefinition(
        "HWW", "High Wind Warning", "weather", "high", "mdi:weather-windy", "#ea580c"
    ),
    "HUA": AlertDefinition(
        "HUA", "Hurricane Watch", "weather", "high", "mdi:hurricane", "#8b5cf6"
    ),
    "HUW": AlertDefinition(
        "HUW", "Hurricane Warning", "weather", "extreme", "mdi:hurricane", "#7c3aed"
    ),
    "HLS": AlertDefinition(
        "HLS",
        "Hurricane Statement",
        "weather",
        "statement",
        "mdi:message-alert",
        "#64748b",
    ),
    "SVA": AlertDefinition(
        "SVA",
        "Severe Thunderstorm Watch",
        "weather",
        "moderate",
        "mdi:weather-lightning",
        "#f59e0b",
    ),
    "SVR": AlertDefinition(
        "SVR",
        "Severe Thunderstorm Warning",
        "weather",
        "high",
        "mdi:weather-lightning-rainy",
        "#ea580c",
    ),
    "SVS": AlertDefinition(
        "SVS",
        "Severe Weather Statement",
        "weather",
        "statement",
        "mdi:message-alert",
        "#64748b",
    ),
    "SQW": AlertDefinition(
        "SQW",
        "Snow Squall Warning",
        "weather",
        "high",
        "mdi:snowflake-alert",
        "#60a5fa",
    ),
    "SMW": AlertDefinition(
        "SMW", "Special Marine Warning", "weather", "high", "mdi:ferry", "#0ea5e9"
    ),
    "SPS": AlertDefinition(
        "SPS",
        "Special Weather Statement",
        "weather",
        "statement",
        "mdi:weather-partly-cloudy-alert",
        "#64748b",
    ),
    "SSA": AlertDefinition(
        "SSA", "Storm Surge Watch", "weather", "high", "mdi:waves-arrow-up", "#0ea5e9"
    ),
    "SSW": AlertDefinition(
        "SSW",
        "Storm Surge Warning",
        "weather",
        "extreme",
        "mdi:waves-arrow-up",
        "#dc2626",
    ),
    "TOA": AlertDefinition(
        "TOA", "Tornado Watch", "weather", "high", "mdi:weather-tornado", "#f97316"
    ),
    "TOR": AlertDefinition(
        "TOR", "Tornado Warning", "weather", "extreme", "mdi:weather-tornado", "#dc2626"
    ),
    "TRA": AlertDefinition(
        "TRA",
        "Tropical Storm Watch",
        "weather",
        "moderate",
        "mdi:weather-hurricane",
        "#8b5cf6",
    ),
    "TRW": AlertDefinition(
        "TRW",
        "Tropical Storm Warning",
        "weather",
        "high",
        "mdi:weather-hurricane",
        "#7c3aed",
    ),
    "TSA": AlertDefinition(
        "TSA", "Tsunami Watch", "weather", "high", "mdi:waves-arrow-up", "#0ea5e9"
    ),
    "TSW": AlertDefinition(
        "TSW", "Tsunami Warning", "weather", "extreme", "mdi:waves-arrow-up", "#dc2626"
    ),
    "WSA": AlertDefinition(
        "WSA", "Winter Storm Watch", "weather", "moderate", "mdi:snowflake", "#93c5fd"
    ),
    "WSW": AlertDefinition(
        "WSW",
        "Winter Storm Warning",
        "weather",
        "high",
        "mdi:snowflake-alert",
        "#60a5fa",
    ),
    "AVA": AlertDefinition(
        "AVA",
        "Avalanche Watch",
        "non_weather",
        "moderate",
        "mdi:image-filter-hdr",
        "#94a3b8",
    ),
    "AVW": AlertDefinition(
        "AVW",
        "Avalanche Warning",
        "non_weather",
        "high",
        "mdi:image-filter-hdr",
        "#dc2626",
    ),
    "BLU": AlertDefinition(
        "BLU", "Blue Alert", "non_weather", "high", "mdi:police-badge", "#2563eb"
    ),
    "CAE": AlertDefinition(
        "CAE",
        "Child Abduction Emergency",
        "non_weather",
        "extreme",
        "mdi:account-alert",
        "#dc2626",
    ),
    "CDW": AlertDefinition(
        "CDW", "Civil Danger Warning", "non_weather", "extreme", "mdi:alert", "#dc2626"
    ),
    "CEM": AlertDefinition(
        "CEM",
        "Civil Emergency Message",
        "non_weather",
        "high",
        "mdi:alert-circle",
        "#ea580c",
    ),
    "EQW": AlertDefinition(
        "EQW",
        "Earthquake Warning",
        "non_weather",
        "extreme",
        "mdi:home-alert",
        "#dc2626",
    ),
    "EVI": AlertDefinition(
        "EVI",
        "Evacuation Immediate",
        "non_weather",
        "extreme",
        "mdi:exit-run",
        "#dc2626",
    ),
    "FRW": AlertDefinition(
        "FRW", "Fire Warning", "non_weather", "high", "mdi:fire-alert", "#ea580c"
    ),
    "HMW": AlertDefinition(
        "HMW",
        "Hazardous Materials Warning",
        "non_weather",
        "high",
        "mdi:biohazard",
        "#ca8a04",
    ),
    "LEW": AlertDefinition(
        "LEW",
        "Law Enforcement Warning",
        "non_weather",
        "high",
        "mdi:police-badge",
        "#1d4ed8",
    ),
    "LAE": AlertDefinition(
        "LAE",
        "Local Area Emergency",
        "non_weather",
        "high",
        "mdi:alert-circle",
        "#ea580c",
    ),
    "TOE": AlertDefinition(
        "TOE",
        "911 Telephone Outage Emergency",
        "non_weather",
        "high",
        "mdi:phone-alert",
        "#ea580c",
    ),
    "NUW": AlertDefinition(
        "NUW",
        "Nuclear Power Plant Warning",
        "non_weather",
        "extreme",
        "mdi:radioactive",
        "#dc2626",
    ),
    "RHW": AlertDefinition(
        "RHW",
        "Radiological Hazard Warning",
        "non_weather",
        "extreme",
        "mdi:radioactive",
        "#dc2626",
    ),
    "SPW": AlertDefinition(
        "SPW",
        "Shelter in Place Warning",
        "non_weather",
        "extreme",
        "mdi:home-lock",
        "#dc2626",
    ),
    "VOW": AlertDefinition(
        "VOW", "Volcano Warning", "non_weather", "high", "mdi:volcano", "#ea580c"
    ),
    "ADR": AlertDefinition(
        "ADR",
        "Administrative Message",
        "administrative",
        "info",
        "mdi:message-text",
        "#64748b",
    ),
    "DMO": AlertDefinition(
        "DMO",
        "Practice/Demo Warning",
        "administrative",
        "test",
        "mdi:test-tube",
        "#6b7280",
    ),
    "RMT": AlertDefinition(
        "RMT",
        "Required Monthly Test",
        "administrative",
        "test",
        "mdi:test-tube",
        "#6b7280",
    ),
    "RWT": AlertDefinition(
        "RWT",
        "Required Weekly Test",
        "administrative",
        "test",
        "mdi:test-tube",
        "#6b7280",
    ),
}
