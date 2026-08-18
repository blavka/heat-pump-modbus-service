from heat_pump_modbus_service.telemetry_filter import TelemetryFilter


def test_temperature_filter_publishes_initial_value_then_suppresses_small_change():
    filtered = TelemetryFilter(temperature_names={"outdoor_temperature"}, temperature_diff=0.2)

    assert filtered.values_to_publish({"outdoor_temperature": 20.0, "unit_status": "off"}) == {
        "outdoor_temperature": 20.0,
        "unit_status": "off",
    }
    assert filtered.values_to_publish({"outdoor_temperature": 20.1, "unit_status": "off"}) == {
        "unit_status": "off",
    }


def test_temperature_filter_publishes_change_at_configured_threshold():
    filtered = TelemetryFilter(temperature_names={"outdoor_temperature"}, temperature_diff=0.2)
    filtered.values_to_publish({"outdoor_temperature": 20.0})

    assert filtered.values_to_publish({"outdoor_temperature": 20.21}) == {"outdoor_temperature": 20.21}
