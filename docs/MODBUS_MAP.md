# Verified Modbus RTU map

## Transport

Derived from **Aermec BMS communication protocol**:

```text
Physical interface: RS-485, two wire
Protocol: Modbus RTU
Baud rate: 9600 bit/s
Framing: 8 data bits, no parity, 1 stop bit (8N1)
Configured device/unit ID: 1
```

The existing installation reaches the RS-485 adapter through the stable host alias `/dev/serial/by-hub/port-2`. The container receives it as `/dev/heat-pump`.

## Holding registers — telemetry

The first implementation reads the contiguous range **117–136** with Modbus function `0x03` / `read_holding_registers`. Entries marked `R` in the protocol are read-only.

| Register | MQTT telemetry name | Protocol/display name | Decode | Notes |
|---:|---|---|---|---|
| 117 | `unit_status` | Unit status | enum | `1=cool`, `2=heat`, `6=hot_water`, `8=off` |
| 118 | `outdoor_temperature` | T-outdoor | signed 16-bit ÷ 10, °C | Outdoor unit |
| 119 | `discharge_temperature` | T-discharge | signed 16-bit ÷ 10, °C | Outdoor unit |
| 120 | `defrost_temperature` | T-defrost | signed 16-bit ÷ 10, °C | Outdoor unit |
| 121 | `suction_temperature` | T-suction | signed 16-bit ÷ 10, °C | Outdoor unit |
| 122 | `economizer_in_temperature` | T-economizer in | signed 16-bit ÷ 10, °C | Outdoor unit |
| 123 | `economizer_out_temperature` | T-economizer out | signed 16-bit ÷ 10, °C | Outdoor unit |
| 124 | `discharge_pressure` | Dis. pressure | signed 16-bit ÷ 10 | Protocol labels its unit inconsistently; do not assign an HA device class until confirmed against the display/manual. |
| 125 | `water_out_temperature` | T-water out PE | signed 16-bit ÷ 10, °C | Leaving water temperature |
| 126 | `optional_water_sensor_temperature` | T-optional water sen. | signed 16-bit ÷ 10, °C | Optional auxiliary-heater leaving-water sensor; can be excluded in YAML if uninstalled. |
| 127 | `water_in_temperature` | T-water in PE | signed 16-bit ÷ 10, °C | Entering water temperature |
| 128 | `tank_control_temperature` | T-tank ctrl. | signed 16-bit ÷ 10, °C | Tank-control temperature |
| 129 | `remote_room_temperature` | T-remote room | signed 16-bit ÷ 10, °C | Excluded at this installation: remote sensor is not wired. |
| 130 | `gas_pipe_temperature` | T-gas pipe | signed 16-bit ÷ 10, °C | Vapor/gas line |
| 131 | `liquid_pipe_temperature` | T-liquid pipe | signed 16-bit ÷ 10, °C | Liquid line |
| 132 | `thermostat` | Thermostat | enum | `1=cool`, `2=heat`, `3=off`; excluded at this installation. |
| 133 | `floor_debug_temperature` | T-floor debug | unsigned integer, °C | Diagnostic feature; prefer hiding unless used. |
| 134 | `debug_time_hours` | Debug time | unsigned integer, hours | Diagnostic feature. |
| 135 | — | Disinfection | enum | Intentionally excluded: unused at this installation. |
| 136 | `floor_debug_error_time_seconds` | Error time for floor debug | unsigned integer, seconds | Diagnostic feature. |
| 137 | `weather_dependent_temperature` | T-weather depend | signed 16-bit ÷ 10, °C | Weather-dependent **target** temperature; verified live as register 137 but not yet included in the initial contiguous 117–136 poll. |

## TUV / space-heating distinction

`unit_status` is the reliable active unit-mode value:

- `2` means the unit is in **space heating**;
- `6` means the unit is producing **domestic hot water (TUV)**;
- `8` is off.

Combined configured modes may still prioritize either heating or DHW. Therefore use `unit_status` for what the unit is actually doing at the time of the poll, rather than only the configured priority coils.

## Weather-dependent target

The operation manual identifies `T-weather depend` as the calculated weather-dependent target temperature shown in the controller's parameter view. It applies for cooling/heating operation, not pure hot-water operation. The live read-only probe returned raw `40`, decoded as `4.0 °C`, while the unit was off. The service polls this register separately and publishes it as `sensor.heat_pump_weather_dependent_temperature`. Confirm the displayed value during active heating before relying on it for dashboards/automations.

This is a read-only calculated target. No supported BMS register/coil for enabling weather-dependent control or changing its curve/setpoints has yet been documented or commissioned for this installation.

## Read-only boundary

The protocol defines write-capable function codes and W/R state variables. This service must not use Modbus write functions (`0x0F`, `0x10`, or single-write equivalents) unless a separate control feature, risk review, YAML opt-in and hardware-safe verification are completed.
