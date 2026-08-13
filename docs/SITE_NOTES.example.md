# Site notes template (not committed with private installation data)

Copy this file to a protected local runbook outside the repository when recording the installation-specific facts.

## Confirmed deployment

- Host and stable serial alias:
- Controller/model and firmware:
- Modbus unit ID:
- Water tank configured:
- Remote sensor physically connected:
- Thermostat control configured:
- Weather-dependent control enabled:

## Display-to-Modbus validation log

| Date/time | Controller display | Modbus register/bit | Observed value | Confirmed by |
|---|---|---|---|---|
| | compressor on/off | bit 80 | | |
| | outdoor fan on/off | bit 81 | | |
| | water pump on/off | bit 175 | | |
| | defrost on/off | bit 86 | | |
| | weather target | register 137 | | |

## Do not place here

Do not commit Wi-Fi details, LAN credentials, MQTT passwords, private keys, Home Assistant tokens, or BMS wiring photos that reveal private site information.
