from heat_pump_modbus_service.commands import CommandProcessor
from heat_pump_modbus_service.controls import MAIN_OPERATION_ON


class Response:
    def __init__(self, registers=None):
        self.registers = registers or []

    def isError(self):
        return False


class Client:
    def __init__(self):
        self.registers = {42: 0x55, 1: 2}
        self.writes = []

    def read_holding_registers(self, address, *, count, device_id):
        return Response([self.registers[address]])

    def write_registers(self, address, values, *, device_id):
        self.registers[address] = values[0]
        self.writes.append((address, values, device_id))
        return Response()


class Publisher:
    def __init__(self):
        self.states = []

    def publish_state(self, name, value):
        self.states.append((name, value))


def test_main_operation_command_updates_modbus_and_publishes_confirmed_state():
    client = Client()
    publisher = Publisher()

    CommandProcessor(client, 1, publisher).handle("heat_pump/utility_room/main_operation/set", b"on")

    assert client.writes == [(42, [MAIN_OPERATION_ON], 1)]
    assert publisher.states == [("main_operation", "on")]
