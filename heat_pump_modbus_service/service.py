"""Read-only polling flow."""
from .controls import MAIN_OPERATION_OFF, MAIN_OPERATION_ON
from .registers import REGISTER_COUNT, decode_registers
from .states import COIL_READ_COUNT, decode_runtime_states
from .telemetry import included_values


def poll_once(client, unit_id: int, publisher, excluded: set[str] | None = None, telemetry_filter=None) -> None:
    """Read documented telemetry and approved runtime-state coils without writes."""
    excluded = excluded or set()
    response = client.read_holding_registers(address=117, count=REGISTER_COUNT, device_id=unit_id)
    if response.isError():
        raise RuntimeError(f"Modbus register read failed: {response}")
    coil_response = client.read_coils(address=0, count=COIL_READ_COUNT, device_id=unit_id)
    if coil_response.isError():
        raise RuntimeError(f"Modbus coil read failed: {coil_response}")
    # Register 137 is the documented calculated weather-dependent target.
    # It is outside the contiguous 117–136 telemetry range, so read it separately.
    weather_response = client.read_holding_registers(address=137, count=1, device_id=unit_id)
    control_mode_response = client.read_holding_registers(address=2, count=1, device_id=unit_id)
    operation_response = client.read_holding_registers(address=42, count=1, device_id=unit_id)
    if weather_response.isError() or control_mode_response.isError() or operation_response.isError():
        raise RuntimeError("Modbus control-state or weather-dependent register read failed")
    values = decode_registers(response.registers) | decode_runtime_states(coil_response.bits)
    raw_weather_temperature = weather_response.registers[0]
    values["weather_dependent_temperature"] = (
        raw_weather_temperature - 65536 if raw_weather_temperature >= 32768 else raw_weather_temperature
    ) / 10
    mode_values = {1: "heat", 2: "hot_water", 4: "heat_and_hot_water"}
    operation = operation_response.registers[0]
    values.update({
        "operation_mode": mode_values.get(control_mode_response.registers[0], f"unknown_{control_mode_response.registers[0]}"),
        "main_operation": "on" if operation == MAIN_OPERATION_ON else "off" if operation == MAIN_OPERATION_OFF else f"unknown_{operation}",
        "quiet_mode": "on" if coil_response.bits[21] else "off",
        "heat_hot_water_priority": "on" if coil_response.bits[20] else "off",
    })
    values = included_values(values, excluded)
    if telemetry_filter is not None:
        values = telemetry_filter.values_to_publish(values)
    for name, value in values.items():
        publisher.publish_state(name, value)
