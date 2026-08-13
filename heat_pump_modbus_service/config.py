"""Validated, deliberately read-only service configuration."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


DEFAULTS: dict[str, Any] = {
    "modbus": {"device": "/dev/heat-pump", "unit_id": 1, "baudrate": 9600, "bytesize": 8, "parity": "N", "stopbits": 1, "timeout_seconds": 3},
    "mqtt": {"host": "127.0.0.1", "port": 1883, "topic_prefix": "heat_pump/utility_room", "discovery_prefix": "homeassistant", "device_name": "Heat Pump", "device_identifier": "heat_pump_utility_room"},
    "runtime": {"poll_interval_seconds": 30, "log_level": "INFO"},
}


def _merge(base: dict[str, Any], supplied: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in supplied.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: Path) -> dict[str, Any]:
    try:
        supplied = yaml.safe_load(path.read_text()) or {}
    except OSError as error:
        raise ConfigError(f"cannot read configuration: {error}") from error
    if not isinstance(supplied, dict):
        raise ConfigError("configuration root must be a mapping")
    if "control" in supplied or "write" in supplied:
        raise ConfigError("this service is read-only; control/write configuration is not supported")
    config = _merge(DEFAULTS, supplied)
    modbus = config["modbus"]
    if not isinstance(modbus["device"], str) or not modbus["device"].startswith("/dev/"):
        raise ConfigError("modbus.device must be an absolute /dev path")
    if modbus["unit_id"] < 1 or modbus["unit_id"] > 247:
        raise ConfigError("modbus.unit_id must be between 1 and 247")
    if config["runtime"]["poll_interval_seconds"] < 5:
        raise ConfigError("runtime.poll_interval_seconds must be at least 5")
    return config
