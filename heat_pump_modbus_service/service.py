"""Read-only polling flow."""
from .registers import REGISTER_COUNT, decode_registers


def poll_once(client, unit_id: int, publisher) -> None:
    response = client.read_holding_registers(address=117, count=REGISTER_COUNT, device_id=unit_id)
    if response.isError():
        raise RuntimeError(f"Modbus read failed: {response}")
    for name, value in decode_registers(response.registers).items():
        publisher.publish_state(name, value)
