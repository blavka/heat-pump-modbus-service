"""Home Assistant MQTT Discovery definitions."""

from __future__ import annotations

import json
from typing import Any

from .registers import _TEMPERATURES
from .states import RUNTIME_STATE_BITS


def discovery_messages(
    *, discovery_prefix: str, topic_prefix: str, device_name: str, device_identifier: str,
    excluded: set[str] | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    excluded = excluded or set()
    device = {"identifiers": [device_identifier], "name": device_name, "manufacturer": "Local Modbus RTU"}
    messages: list[tuple[str, dict[str, Any]]] = []
    for name in _TEMPERATURES.values():
        if name in excluded:
            continue
        payload: dict[str, Any] = {
            "name": name.replace("_", " ").title(),
            "unique_id": f"{device_identifier}_{name}",
            "state_topic": f"{topic_prefix}/{name}/state",
            "availability_topic": f"{topic_prefix}/availability",
            "device": device,
            "device_class": "temperature",
            "state_class": "measurement",
            "unit_of_measurement": "°C",
        }
        messages.append((f"{discovery_prefix}/sensor/{device_identifier}_{name}/config", payload))
    for name in RUNTIME_STATE_BITS.values():
        if name in excluded:
            continue
        payload = {
            "name": name.replace("_", " ").title(),
            "unique_id": f"{device_identifier}_{name}",
            "state_topic": f"{topic_prefix}/{name}/state",
            "availability_topic": f"{topic_prefix}/availability",
            "payload_on": "on",
            "payload_off": "off",
            "device": device,
        }
        if name in {"compressor_running", "outdoor_fan_running", "heat_pump_water_pump_running"}:
            payload["device_class"] = "running"
        messages.append((f"{discovery_prefix}/binary_sensor/{device_identifier}_{name}/config", payload))
    for name in ("unit_status", "thermostat"):
        if name in excluded:
            continue
        payload = {
            "name": name.replace("_", " ").title(),
            "unique_id": f"{device_identifier}_{name}",
            "state_topic": f"{topic_prefix}/{name}/state",
            "availability_topic": f"{topic_prefix}/availability",
            "device": device,
        }
        messages.append((f"{discovery_prefix}/sensor/{device_identifier}_{name}/config", payload))
    return messages


def encode(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
