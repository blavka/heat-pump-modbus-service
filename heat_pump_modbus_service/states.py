"""Approved read-only runtime state bits from the documented BMS coil map."""

from __future__ import annotations

RUNTIME_STATE_BITS = {
    80: "compressor_running",
    81: "outdoor_fan_running",
    86: "defrosting",
    173: "tank_heater_running",
    175: "heat_pump_water_pump_running",
}

COIL_READ_COUNT = max(RUNTIME_STATE_BITS) + 1


def decode_runtime_states(bits: list[bool]) -> dict[str, bool]:
    """Decode explicitly approved read-only runtime states; never control coils."""
    if len(bits) < COIL_READ_COUNT:
        raise ValueError(f"expected at least {COIL_READ_COUNT} coil bits, got {len(bits)}")
    return {name: bool(bits[address]) for address, name in RUNTIME_STATE_BITS.items()}
