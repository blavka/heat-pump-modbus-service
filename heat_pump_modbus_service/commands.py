"""Translate restricted MQTT command topics into verified Modbus controls."""

from __future__ import annotations

from .controls import (
    set_heat_hot_water_priority,
    set_main_operation,
    set_mode,
    set_quiet_mode,
    set_weather_dependent_control,
)


class CommandProcessor:
    def __init__(self, client, unit_id: int, publisher) -> None:
        self.client = client
        self.unit_id = unit_id
        self.publisher = publisher

    def handle(self, topic: str, payload: bytes) -> None:
        command = payload.decode("utf-8").strip().lower()
        if topic.endswith("/main_operation/set"):
            enabled = command == "on"
            if command not in {"on", "off"}:
                raise ValueError("main operation command must be on or off")
            set_main_operation(self.client, self.unit_id, enabled)
            self.publisher.publish_state("main_operation", "on" if enabled else "off")
        elif topic.endswith("/quiet_mode/set"):
            enabled = command == "on"
            if command not in {"on", "off"}:
                raise ValueError("quiet mode command must be on or off")
            set_quiet_mode(self.client, self.unit_id, enabled)
            self.publisher.publish_state("quiet_mode", "on" if enabled else "off")
        elif topic.endswith("/weather_dependent_control/set"):
            enabled = command == "on"
            if command not in {"on", "off"}:
                raise ValueError("weather-dependent control command must be on or off")
            set_weather_dependent_control(self.client, self.unit_id, enabled)
            self.publisher.publish_state("weather_dependent_control", "on" if enabled else "off")
        elif topic.endswith("/heat_hot_water_priority/set"):
            enabled = command == "on"
            if command not in {"on", "off"}:
                raise ValueError("priority command must be on or off")
            set_heat_hot_water_priority(self.client, self.unit_id, enabled)
            self.publisher.publish_state("heat_hot_water_priority", "on" if enabled else "off")
        elif topic.endswith("/operation_mode/set"):
            set_mode(self.client, self.unit_id, command)
            self.publisher.publish_state("operation_mode", command)
        else:
            raise ValueError(f"unsupported command topic: {topic}")
