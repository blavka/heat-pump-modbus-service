from heat_pump_modbus_service.mqtt import publish_retained


class PublishInfo:
    def __init__(self):
        self.waited = False

    def wait_for_publish(self):
        self.waited = True


class Client:
    def __init__(self):
        self.info = PublishInfo()
        self.calls = []

    def publish(self, topic, payload, *, qos, retain):
        self.calls.append((topic, payload, qos, retain))
        return self.info


def test_publish_retained_waits_for_mqtt_delivery():
    client = Client()

    publish_retained(client, "homeassistant/sensor/example/config", "{}")

    assert client.calls == [("homeassistant/sensor/example/config", "{}", 1, True)]
    assert client.info.waited is True
