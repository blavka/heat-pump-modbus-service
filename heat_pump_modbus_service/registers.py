"""Known read-only holding-register map for the initially supported heat pump."""

from __future__ import annotations

REGISTER_COUNT = 20

_STATUS = {1: "cool", 2: "heat", 6: "hot_water", 8: "off"}
_THERMOSTAT = {1: "cool", 2: "heat", 3: "off"}

_TEMPERATURES = {
    118: "outdoor_temperature",
    119: "discharge_temperature",
    120: "defrost_temperature",
    121: "suction_temperature",
    122: "economizer_in_temperature",
    123: "economizer_out_temperature",
    124: "discharge_pressure",
    125: "water_out_temperature",
    126: "optional_water_sensor_temperature",
    127: "water_in_temperature",
    128: "tank_control_temperature",
    129: "remote_room_temperature",
    130: "gas_pipe_temperature",
    131: "liquid_pipe_temperature",
    137: "weather_dependent_temperature",
}


def _signed_16(value: int) -> int:
    return value - 65536 if value >= 32768 else value


def decode_registers(registers: list[int]) -> dict[str, str | float | int]:
    """Decode holding registers 117 through 136 from one Modbus response.

    The intentionally omitted disinfection register is unused at this site.
    """
    if len(registers) != REGISTER_COUNT:
        raise ValueError(f"expected {REGISTER_COUNT} registers (117-136), got {len(registers)}")

    values: dict[str, str | float | int] = {
        "unit_status": _STATUS.get(registers[0], f"unknown_{registers[0]}"),
        "thermostat": _THERMOSTAT.get(registers[15], f"unknown_{registers[15]}"),
        "floor_debug_temperature": registers[16],
        "debug_time_hours": registers[17],
        "floor_debug_error_time_seconds": registers[19],
    }
    for address, name in _TEMPERATURES.items():
        if address <= 136:
            values[name] = _signed_16(registers[address - 117]) / 10
    return values
