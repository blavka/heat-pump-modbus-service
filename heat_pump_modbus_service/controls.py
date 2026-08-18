"""Validated Modbus control primitives for the verified heat-pump command map."""

from __future__ import annotations

import time

MODE_VALUES = {
    "heat": 1,
    "hot_water": 2,
    "heat_and_hot_water": 4,
}
MAIN_OPERATION_ON = 0xAA
MAIN_OPERATION_OFF = 0x55


class ControlError(RuntimeError):
    """A control command could not be safely applied."""


def _read_register(client, address: int, unit_id: int) -> int:
    response = client.read_holding_registers(address, count=1, device_id=unit_id)
    if response.isError():
        raise ControlError(f"cannot read holding register {address}")
    return response.registers[0]


def _write_register(client, address: int, value: int, unit_id: int) -> None:
    response = client.write_registers(address, [value], device_id=unit_id)
    if response.isError():
        raise ControlError(f"cannot write holding register {address}")
    for attempt in range(10):
        if _read_register(client, address, unit_id) == value:
            return
        if attempt < 9:
            time.sleep(1)
    raise ControlError(f"holding register {address} did not confirm the requested value")


def set_main_operation(client, unit_id: int, enabled: bool) -> None:
    """Set BMS Word 42 to the documented ON/OFF command and confirm it."""
    _write_register(client, 42, MAIN_OPERATION_ON if enabled else MAIN_OPERATION_OFF, unit_id)


def _write_coil(client, address: int, value: bool, unit_id: int) -> None:
    response = client.write_coil(address, value, device_id=unit_id)
    if response.isError():
        raise ControlError(f"cannot write coil {address}")
    for attempt in range(5):
        readback = client.read_coils(address, count=1, device_id=unit_id)
        if not readback.isError() and bool(readback.bits[0]) == value:
            return
        if attempt < 4:
            time.sleep(1)
    raise ControlError(f"coil {address} did not confirm the requested value")


def set_quiet_mode(client, unit_id: int, enabled: bool) -> None:
    """Set documented Quiet Mode coil 21 and confirm it."""
    _write_coil(client, 21, enabled, unit_id)


def set_heat_hot_water_priority(client, unit_id: int, hot_water_priority: bool) -> None:
    """Set Heat+Hot Water Priority coil 20 only while the heat pump is off."""
    if _read_register(client, 42, unit_id) != MAIN_OPERATION_OFF:
        raise ControlError("cannot change heating/hot-water priority while main operation is on")
    _write_coil(client, 20, hot_water_priority, unit_id)


def set_mode(client, unit_id: int, mode: str) -> None:
    """Set an approved non-cooling mode only while the heat pump is off."""
    if mode not in MODE_VALUES:
        raise ControlError(f"unsupported mode: {mode}")
    if _read_register(client, 42, unit_id) != MAIN_OPERATION_OFF:
        raise ControlError("cannot change mode while main operation is on")
    # The controller's live map exposes the documented Mode word at Modbus address 2.
    _write_register(client, 2, MODE_VALUES[mode], unit_id)
