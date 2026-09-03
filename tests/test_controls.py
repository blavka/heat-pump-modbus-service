import pytest

from heat_pump_modbus_service.controls import (
    ControlError,
    MAIN_OPERATION_ON,
    set_heat_hot_water_priority,
    set_main_operation,
    set_mode,
    set_quiet_mode,
    set_weather_dependent_control,
)


class Response:
    def __init__(self, registers=None, bits=None, error=False):
        self.registers = registers or []
        self.bits = bits or []
        self.error = error

    def isError(self):
        return self.error


class RunningClient:
    def __init__(self):
        self.writes = []

    def read_holding_registers(self, address, *, count, device_id):
        assert (address, count, device_id) == (42, 1, 1)
        return Response(registers=[0xAA])

    def write_registers(self, address, values, *, device_id):
        self.writes.append((address, values, device_id))
        return Response()


def test_mode_change_is_refused_when_main_operation_is_on():
    client = RunningClient()

    with pytest.raises(ControlError, match="main operation is on"):
        set_mode(client, 1, "heat_and_hot_water")

    assert client.writes == []


def test_mode_uses_verified_register_two_and_confirms_readback():
    client = OffClient()
    client.registers[2] = 2

    set_mode(client, 1, "heat_and_hot_water")

    assert client.writes == [(2, [4], 1)]


class OffClient:
    def __init__(self):
        self.registers = {42: 0x55}
        self.writes = []

    def read_holding_registers(self, address, *, count, device_id):
        return Response(registers=[self.registers[address]])

    def write_registers(self, address, values, *, device_id):
        self.writes.append((address, values, device_id))
        self.registers[address] = values[0]
        return Response()


def test_main_operation_writes_documented_on_value_and_confirms_readback():
    client = OffClient()

    set_main_operation(client, 1, True)

    assert client.writes == [(42, [MAIN_OPERATION_ON], 1)]
    assert client.registers[42] == MAIN_OPERATION_ON


class DelayedRegisterClient(OffClient):
    def __init__(self):
        super().__init__()
        self.registers[2] = 2
        self.pending_value = None
        self.reads_after_write = 0

    def read_holding_registers(self, address, *, count, device_id):
        if address == 2 and self.pending_value is not None:
            self.reads_after_write += 1
            if self.reads_after_write >= 3:
                self.registers[2] = self.pending_value
        return Response(registers=[self.registers[address]])

    def write_registers(self, address, values, *, device_id):
        self.writes.append((address, values, device_id))
        self.pending_value = values[0]
        return Response()


def test_mode_waits_for_delayed_register_confirmation(monkeypatch):
    monkeypatch.setattr("heat_pump_modbus_service.controls.time.sleep", lambda _seconds: None)
    client = DelayedRegisterClient()

    set_mode(client, 1, "heat")

    assert client.registers[2] == 1
    assert client.reads_after_write == 3


class ControlClient(OffClient):
    def __init__(self):
        super().__init__()
        self.registers[1] = 2
        self.coils = {20: True, 21: True, 22: False}
        self.coil_writes = []

    def read_coils(self, address, *, count, device_id):
        return Response(bits=[self.coils[address]])

    def write_coil(self, address, value, *, device_id):
        self.coil_writes.append((address, value, device_id))
        self.coils[address] = value
        return Response()


def test_quiet_mode_and_heating_hot_water_priority_write_and_confirm_when_off():
    client = ControlClient()

    set_quiet_mode(client, 1, False)
    set_weather_dependent_control(client, 1, True)
    set_heat_hot_water_priority(client, 1, False)

    assert client.coil_writes == [(21, False, 1), (22, True, 1), (20, False, 1)]
    assert client.coils == {20: False, 21: False, 22: True}
