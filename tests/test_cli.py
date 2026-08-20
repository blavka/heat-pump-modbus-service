from heat_pump_modbus_service.cli import MqttPublisher


class PublishInfo:
    def wait_for_publish(self):
        pass


class Client:
    def __init__(self):
        self.calls = []

    def publish(self, topic, payload, *, qos, retain):
        self.calls.append((topic, payload, qos, retain))
        return PublishInfo()


def test_mqtt_publisher_encodes_boolean_state_for_home_assistant_binary_sensor():
    client = Client()

    MqttPublisher(client, "heat_pump/utility_room").publish_state("compressor_running", True)

    assert client.calls == [
        ("heat_pump/utility_room/compressor_running/state", "on", 1, True),
    ]

def test_mqtt_publisher_encodes_false_boolean_state_for_home_assistant_binary_sensor():
    client = Client()

    MqttPublisher(client, "heat_pump/utility_room").publish_state("compressor_running", False)

    assert client.calls == [
        ("heat_pump/utility_room/compressor_running/state", "off", 1, True),
    ]
