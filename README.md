# heat-pump-modbus-service

A small, local and **read-only** Modbus RTU telemetry bridge for heat pumps. It publishes retained MQTT state and Home Assistant MQTT Discovery configuration.

## Compatibility

The initial deployment and live Modbus verification are for an **ARGOS EN MO160**. The same controller/BMS register map is intended for the related **ARGOS EN MO100** variants as well. Before deploying to another unit, confirm its controller BMS documentation, Modbus unit ID, serial framing, and the read-only register map with a no-write probe.

The initial register map uses Modbus RTU at 9600 8N1, unit ID 1 and holding registers 117–136.

## Safety model

- This service contains **no Modbus write implementation**.
- YAML control/write options are rejected during validation.
- The container receives one serial device only, has no Linux capabilities, uses a read-only root filesystem and runs as an unprivileged user.
- The legacy `Disinfection` register is intentionally not published because it is unused in this installation.

## Installation

```sh
cp config/config.example.yaml config/local.yaml
DIALOUT_GID=$(getent group dialout | cut -d: -f3)
printf 'DIALOUT_GID=%s\n' "$DIALOUT_GID" > .env
sudo chown root:10003 config/local.yaml
sudo chmod 640 config/local.yaml
docker compose up -d --build
docker compose ps
docker compose logs -f heat-pump-modbus-service
```

The Compose example maps `/dev/serial/by-hub/port-2`, a host udev alias tied to the physical middle USB-hub port, to `/dev/heat-pump` in the container. Do not replace it with unstable `/dev/ttyUSB<n>` numbering.

## Configuration validation

```sh
uv run heat-pump-modbus-service --config config/local.yaml validate-config
uv run heat-pump-modbus-service --config config/local.yaml run --once
```

## MQTT and Home Assistant

State topics use the configured `mqtt.topic_prefix`, for example:

```text
heat_pump/utility_room/outdoor_temperature/state
heat_pump/utility_room/water_out_temperature/state
heat_pump/utility_room/unit_status/state
heat_pump/utility_room/availability
```

Discovery configuration is retained under `homeassistant/sensor/.../config`. The service publishes online availability only after MQTT connects and uses retained offline MQTT last-will state.

## Development

```sh
uv run --with pytest pytest -q
```

License: MIT.
