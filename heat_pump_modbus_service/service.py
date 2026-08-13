"""Read-only polling flow."""
from .registers import REGISTER_COUNT, decode_registers
from .states import COIL_READ_COUNT, decode_runtime_states
from .telemetry import included_values


def poll_once(client, unit_id: int, publisher, excluded: set[str] | None = None) -> None:
    """Read documented telemetry and approved runtime-state coils without writes."""
    excluded = excluded or set()
    response = client.read_holding_registers(address=117, count=REGISTER_COUNT, device_id=unit_id)
    if response.isError():
        raise RuntimeError(f"Modbus register read failed: {response}")
    coil_response = client.read_coils(address=0, count=COIL_READ_COUNT, device_id=unit_id)
    if coil_response.isError():
        raise RuntimeError(f"Modbus coil read failed: {coil_response}")
    values = decode_registers(response.registers) | decode_runtime_states(coil_response.bits)
    for name, value in included_values(values, excluded).items():
        publisher.publish_state(name, value)
