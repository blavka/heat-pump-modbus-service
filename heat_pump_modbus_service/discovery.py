"""Home Assistant MQTT Discovery definitions."""

from __future__ import annotations

import json
from typing import Any

from .registers import _TEMPERATURES


def discovery_messages(
    *, discovery_prefix: str, topic_prefix: str, device_name: str, device_identifier: str
) -> list[tuple[str, dict[str, Any]]]:
    device = {"identifiers": [device_identifier], "name": device_name, "manufacturer": "Local Modbus RTU"}
    messages: list[tuple[str, dict[str, Any]]] = []
    for name in _TEMPERATURES.values():
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
    for name in ("unit_status", "thermostat"):
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
