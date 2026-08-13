# Status and configuration bit map

The BMS protocol stores bit variables at addresses 0–199 and exposes read-coil function `0x01`. A live read of bits 0–191 from the current controller succeeded.

## Critical distinction

The protocol mixes two classes of bits:

1. **runtime state bits** marked `R` — safe candidates for future read-only Home Assistant binary sensors;
2. **configuration/control bits** marked `W/R` — readable, but potentially change a controller setting if written.

The project must publish only confirmed `R` runtime bits by default. No coil write support is currently implemented.

## Confirmed configuration bits — do not expose as controls yet

| Bit | Protocol label | Meaning when `1` | Current observed value |
|---:|---|---|---|
| 19 | Cool+Hot Water Priority | Hot water has priority over cooling | on |
| 20 | Heat+Hot Water Priority | Hot water has priority over heating | on |
| 21 | Quiet Mode | Quiet Mode enabled | off |
| 22 | Weather depend | Weather-dependent control enabled | not yet sampled individually |
| 23 | Disinfection | Disinfection enabled | not used |
| 29 | Water Tank | Tank configured/present | on |
| 33 | Remote sensor | Remote sensor configured/present | expected off here; verify live before documenting as site fact |

The old proof of concept contained `write_coil(21, True)` and the manual confirms Quiet Mode can be enabled/disabled/timed from the panel. That supports the interpretation of bit 21, but it does **not** authorize a remote HA control yet.

The active values seen during the initial read — bits `19`, `20`, and `29` — are configuration/priority flags, not proof that a fan or pump is running.

## Read-only runtime states suitable for future telemetry

| Bit | Protocol label | `1` means | Recommended HA entity |
|---:|---|---|---|
| 80 | Compressor State | Compressor on | `binary_sensor.compressor_running` |
| 81 | ODU Fan State | Outdoor fan on | `binary_sensor.outdoor_fan_running` |
| 83 | 4-way Valve State | Valve energized | diagnostic binary sensor |
| 84 | Compressor Crankcase Heater State | Heater on | diagnostic binary sensor |
| 85 | Underpan Heater State | Heater on | diagnostic binary sensor |
| 86 | Defrosting State | Defrosting active | `binary_sensor.defrosting` |
| 87 | Oil Return State | Oil-return cycle active | diagnostic binary sensor |
| 169 | Other Heat Source State | Other heat source on | diagnostic binary sensor |
| 170 | Flow Switch State | Flow switch open | diagnostic binary sensor; verify polarity in the UI |
| 171 | IDU E-heater 1 State | Internal electric heater 1 on | diagnostic binary sensor |
| 172 | IDU E-heater 2 State | Internal electric heater 2 on | diagnostic binary sensor |
| 173 | Water Tank Heater State | TUV tank heater on | `binary_sensor.tank_heater_running` |
| 175 | IDU Water Pump State | Internal water pump on | `binary_sensor.heat_pump_water_pump_running` |
| 176 | Circulating 2-way Valve State | Valve on | diagnostic binary sensor |

## Read-only faults/protections

The same map has fault/protection bits, including outdoor sensor/fan faults (88–98), high/low-pressure and high-discharge protections (94–96), system protections (102 onward), water-flow protection (188), and indoor recoverable/irrecoverable protection (190–191).

Expose these only after the application has a declared, tested error strategy. A raw `on` binary sensor must not be silently presented as a benign state; it should use diagnostic category and an appropriate problem-class entity.

## Next implementation slice

A safe next telemetry-only feature is a YAML-controlled list of *approved read-only* state bits, defaulting to disabled. First candidates are `80`, `81`, `86`, `173`, and `175`. Verify each against the controller display while the equipment changes state before making it a default entity.
