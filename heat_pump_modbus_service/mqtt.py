"""MQTT delivery helpers."""


def publish_retained(client, topic: str, payload: str) -> None:
    info = client.publish(topic, payload, qos=1, retain=True)
    info.wait_for_publish()
