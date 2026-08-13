from heat_pump_modbus_service.states import RUNTIME_STATE_BITS, decode_runtime_states


def test_decodes_only_approved_read_only_runtime_state_bits():
    bits = [False] * 192
    bits[80] = True
    bits[81] = True
    bits[86] = True
    bits[173] = True
    bits[175] = True
    bits[21] = True  # Quiet Mode is writable configuration and must not be telemetry.

    values = decode_runtime_states(bits)

    assert values == {
        "compressor_running": True,
        "outdoor_fan_running": True,
        "defrosting": True,
        "tank_heater_running": True,
        "heat_pump_water_pump_running": True,
    }
    assert set(RUNTIME_STATE_BITS) == {80, 81, 86, 173, 175}


def test_rejects_short_coil_response():
    try:
        decode_runtime_states([False] * 175)
    except ValueError as error:
        assert "176" in str(error)
    else:
        raise AssertionError("expected ValueError")
