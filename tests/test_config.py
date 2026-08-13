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
    assert config["runtime"]["poll_interval_seconds"] == 30


def test_rejects_any_write_control_configuration(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("control:\n  enabled: true\n")

    with pytest.raises(ConfigError, match="read-only"):
        load_config(config_file)
