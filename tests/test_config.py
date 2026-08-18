from pathlib import Path

import pytest

from heat_pump_modbus_service.config import ConfigError, load_config


def test_loads_read_only_modbus_configuration(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
modbus:
  device: /dev/serial/by-hub/port-2
  unit_id: 1
mqtt:
  topic_prefix: heat_pump/utility_room
"""
    )

    config = load_config(config_file)

    assert config["modbus"]["baudrate"] == 9600
    assert config["runtime"]["poll_interval_seconds"] == 5
    assert config["telemetry"]["temperature_diff"] == 0.2


def test_accepts_explicit_control_enablement(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("control:\n  enabled: true\n")

    assert load_config(config_file)["control"]["enabled"] is True
