from heat_pump_modbus_service.discovery import discovery_messages


def test_discovery_publishes_temperature_and_status_entities_only():
    messages = discovery_messages(
        discovery_prefix="homeassistant",
        topic_prefix="heat_pump/utility_room",
        device_name="Heat Pump",
        device_identifier="heat_pump_utility_room",
        excluded={"thermostat", "remote_room_temperature"},
    )

    topics = {topic for topic, _payload in messages}
    assert "homeassistant/sensor/heat_pump_utility_room_outdoor_temperature/config" in topics
    assert "homeassistant/sensor/heat_pump_utility_room_unit_status/config" in topics
    assert "homeassistant/sensor/heat_pump_utility_room_thermostat/config" not in topics
    assert "homeassistant/sensor/heat_pump_utility_room_remote_room_temperature/config" not in topics
    assert all("disinfection" not in topic for topic in topics)

    outdoor_payload = dict(messages)[
        "homeassistant/sensor/heat_pump_utility_room_outdoor_temperature/config"
    ]
    assert outdoor_payload["state_topic"] == "heat_pump/utility_room/outdoor_temperature/state"
    assert outdoor_payload["unit_of_measurement"] == "°C"
    weather_payload = dict(messages)[
        "homeassistant/sensor/heat_pump_utility_room_weather_dependent_temperature/config"
    ]
    assert weather_payload["name"] == "Weather-Compensated Target Temperature"


def test_discovery_adds_only_requested_non_cooling_controls():
    messages = discovery_messages(
        discovery_prefix="homeassistant",
        topic_prefix="heat_pump/utility_room",
        device_name="Heat Pump",
        device_identifier="heat_pump_utility_room",
        controls_enabled=True,
    )
    payloads = dict(messages)

    assert "homeassistant/switch/heat_pump_utility_room_main_operation/config" in payloads
    assert "homeassistant/switch/heat_pump_utility_room_quiet_mode/config" in payloads
    weather_control = payloads[
        "homeassistant/switch/heat_pump_utility_room_weather_dependent_control/config"
    ]
    assert weather_control["name"] == "Weather-Compensated Control"
    assert "homeassistant/switch/heat_pump_utility_room_heat_hot_water_priority/config" in payloads
    mode = payloads["homeassistant/select/heat_pump_utility_room_operation_mode/config"]
    assert mode["options"] == ["heat", "hot_water", "heat_and_hot_water"]
    assert all("cool" not in topic for topic in payloads)
