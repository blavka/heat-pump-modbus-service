from heat_pump_modbus_service.discovery import discovery_messages


def test_discovery_publishes_approved_runtime_states_as_binary_sensors():
    messages = discovery_messages(
        discovery_prefix="homeassistant",
        topic_prefix="heat_pump/utility_room",
        device_name="Heat Pump",
        device_identifier="heat_pump_utility_room",
    )

    topic = "homeassistant/binary_sensor/heat_pump_utility_room_compressor_running/config"
    payload = dict(messages)[topic]

    assert payload["state_topic"] == "heat_pump/utility_room/compressor_running/state"
    assert payload["payload_on"] == "on"
    assert payload["payload_off"] == "off"
    assert payload["device_class"] == "running"
    assert all("quiet" not in message_topic for message_topic, _ in messages)
