from heat_pump_modbus_service.discovery import discovery_messages


def test_discovery_publishes_temperature_and_status_entities_only():
    messages = discovery_messages(
        discovery_prefix="homeassistant",
        topic_prefix="heat_pump/utility_room",
        device_name="Heat Pump",
        device_identifier="heat_pump_utility_room",
    )

    topics = {topic for topic, _payload in messages}
    assert "homeassistant/sensor/heat_pump_utility_room_outdoor_temperature/config" in topics
    assert "homeassistant/sensor/heat_pump_utility_room_unit_status/config" in topics
    assert all("disinfection" not in topic for topic in topics)

    outdoor_payload = dict(messages)[
        "homeassistant/sensor/heat_pump_utility_room_outdoor_temperature/config"
    ]
    assert outdoor_payload["state_topic"] == "heat_pump/utility_room/outdoor_temperature/state"
    assert outdoor_payload["unit_of_measurement"] == "°C"
