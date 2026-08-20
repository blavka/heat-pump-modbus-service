"""CLI and runtime entrypoint for the read-only heat-pump telemetry bridge."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import click
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusSerialClient

from .command_queue import CommandQueue
from .commands import CommandProcessor
from .config import ConfigError, load_config
from .discovery import discovery_messages, encode
from .mqtt import publish_retained
from .telemetry_filter import TelemetryFilter
from .registers import _TEMPERATURES
from .service import poll_once


class MqttPublisher:
    def __init__(self, client: mqtt.Client, topic_prefix: str):
        self.client = client
        self.topic_prefix = topic_prefix

    def publish_state(self, name: str, value: object) -> None:
        payload = "on" if value is True else "off" if value is False else str(value).lower()
        publish_retained(self.client, f"{self.topic_prefix}/{name}/state", payload)


def _client(config: dict) -> ModbusSerialClient:
    m = config["modbus"]
    return ModbusSerialClient(
        port=m["device"], baudrate=m["baudrate"], bytesize=m["bytesize"],
        parity=m["parity"], stopbits=m["stopbits"], timeout=m["timeout_seconds"],
    )


@click.group()
@click.option("--config", "config_path", type=click.Path(path_type=Path), required=True)
@click.pass_context
def main(ctx: click.Context, config_path: Path) -> None:
    """Read only Modbus RTU telemetry service for heat pumps."""
    try:
        ctx.obj = load_config(config_path)
    except ConfigError as error:
        raise click.ClickException(str(error)) from error


@main.command("validate-config")
@click.pass_context
def validate_config(ctx: click.Context) -> None:
    """Validate YAML without connecting to Modbus or MQTT."""
    click.echo("configuration valid; write/control features are unavailable by design")


@main.command()
@click.option("--once", is_flag=True, help="Poll once and exit after retained state publication.")
@click.pass_context
def run(ctx: click.Context, once: bool) -> None:
    """Publish read-only telemetry and Home Assistant MQTT Discovery."""
    config = ctx.obj
    logging.basicConfig(level=config["runtime"]["log_level"], format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    mc = config["mqtt"]
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=mc["device_identifier"])
    client.will_set(f"{mc['topic_prefix']}/availability", "offline", retain=True)
    client.connect(mc["host"], mc["port"], keepalive=60)
    client.loop_start()
    publisher = MqttPublisher(client, mc["topic_prefix"])
    telemetry_filter = TelemetryFilter(
        temperature_names={name for name in _TEMPERATURES.values() if "temperature" in name},
        temperature_diff=config["telemetry"]["temperature_diff"],
    )
    try:
        for topic, payload in discovery_messages(
            discovery_prefix=mc["discovery_prefix"], topic_prefix=mc["topic_prefix"],
            device_name=mc["device_name"], device_identifier=mc["device_identifier"],
            excluded=set(config["telemetry"]["excluded"]),
            controls_enabled=config["control"]["enabled"],
        ):
            publish_retained(client, topic, encode(payload))
        publish_retained(client, f"{mc['topic_prefix']}/availability", "online")
        modbus = _client(config)
        if not modbus.connect():
            raise click.ClickException(f"cannot open Modbus device {config['modbus']['device']}")
        try:
            command_queue: CommandQueue | None = None
            if config["control"]["enabled"]:
                processor = CommandProcessor(modbus, config["modbus"]["unit_id"], publisher)

                def handle_command(topic: str, payload: bytes) -> None:
                    try:
                        processor.handle(topic, payload)
                        logger.info("applied heat-pump control command for %s", topic)
                    except Exception:
                        logger.exception("rejected heat-pump control command for %s", topic)

                command_queue = CommandQueue(handle_command)

                def on_message(_client, _userdata, message) -> None:
                    command_queue.enqueue(message.topic, message.payload)

                client.on_message = on_message
                client.subscribe(f"{mc['topic_prefix']}/+/set", qos=1)
            while True:
                if command_queue is not None:
                    command_queue.drain()
                poll_once(
                    modbus, config["modbus"]["unit_id"], publisher,
                    excluded=set(config["telemetry"]["excluded"]),
                    telemetry_filter=telemetry_filter,
                )
                logger.info("published heat-pump telemetry")
                if once:
                    break
                if command_queue is None:
                    time.sleep(config["runtime"]["poll_interval_seconds"])
                else:
                    command_queue.wait_for_work(config["runtime"]["poll_interval_seconds"])
        finally:
            modbus.close()
    finally:
        client.disconnect()
        client.loop_stop()
