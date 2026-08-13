from heat_pump_modbus_service.service import poll_once


class Response:
    registers = [8, 264, 298, 279, 297, 293, 293, 280, 278, 65236, 280, 607, 0, 289, 276, 3, 65436, 0, 0, 0]

    def isError(self):
        return False


class CoilResponse:
    bits = [False] * 192

    def isError(self):
        return False


class Client:
    def read_holding_registers(self, *, address, count, device_id):
        assert (address, count, device_id) == (117, 20, 1)
        return Response()

    def read_coils(self, *, address, count, device_id):
        assert (address, count, device_id) == (0, 176, 1)
        response = CoilResponse()
        response.bits[80] = True
        response.bits[175] = True
        return response


class Publisher:
    def __init__(self):
        self.published = []

    def publish_state(self, name, value):
        self.published.append((name, value))


def test_poll_once_reads_known_range_and_publishes_decoded_values():
    publisher = Publisher()

    poll_once(Client(), 1, publisher)

    assert ("unit_status", "off") in publisher.published
    assert ("outdoor_temperature", 26.4) in publisher.published
    assert ("compressor_running", True) in publisher.published
    assert ("heat_pump_water_pump_running", True) in publisher.published
    assert all(name != "disinfection" for name, _value in publisher.published)
