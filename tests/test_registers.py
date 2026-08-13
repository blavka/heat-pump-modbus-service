from heat_pump_modbus_service.registers import decode_registers


def test_decodes_confirmed_read_only_heat_pump_registers():
    raw = [8, 264, 298, 279, 297, 293, 293, 280, 278, 65236, 280, 607, 0, 289, 276, 3, 65436, 0, 0, 0]

    values = decode_registers(raw)

    assert values["unit_status"] == "off"
    assert values["outdoor_temperature"] == 26.4
    assert values["water_out_temperature"] == 27.8
    assert values["water_in_temperature"] == 28.0
    assert values["tank_control_temperature"] == 60.7
    assert values["thermostat"] == "off"
    assert "disinfection" not in values


def test_rejects_incomplete_register_response():
    try:
        decode_registers([8])
    except ValueError as error:
        assert "20" in str(error)
    else:
        raise AssertionError("expected ValueError")
