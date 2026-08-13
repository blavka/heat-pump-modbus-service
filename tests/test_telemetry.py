from pathlib import Path

from heat_pump_modbus_service.config import load_config
from heat_pump_modbus_service.telemetry import included_values


def test_excludes_configured_telemetry_from_discovery_and_state(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
telemetry:
  excluded:
    - thermostat
    - remote_room_temperature
"""
    )
    config = load_config(config_file)

    values = included_values(
        {"thermostat": "off", "remote_room_temperature": 20.0, "water_out_temperature": 31.5},
        config["telemetry"]["excluded"],
    )

    assert values == {"water_out_temperature": 31.5}
