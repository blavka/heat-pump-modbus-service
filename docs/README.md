# Documentation

This directory contains implementation notes derived from the locally supplied equipment documentation. The PDFs themselves are not copied into this repository: they are vendor documents and deployment evidence, not source code.

## Sources reviewed

| Source document | Use in this project |
|---|---|
| `aermec/BMS communication protocol.pdf` | Authoritative Modbus RTU framing, read/write access types, holding-register map, coil/state-bit map. |
| `argo/aghp081ph.pdf` | User-interface labels and status/parameter viewing names. |
| `UM-OPERATION-INSTRUCTIONS-3D-SMART-EN-R00.pdf` | Comparable controller user manual; confirms Quiet Mode and weather-dependent behavior. |
| `aermec/Directions for use.pdf` | Comparable user guide. |
| `aermec/Data sheet.pdf` | Product data; not used for Modbus mapping. |
| `Tepelné čerpadlo. vzduch _ voda MONOBLOK. modely ARGOS EN MO120 _ ARGOS EN MO160. Návod na instalaci.pdf` | Czech installation reference; not used as Modbus-map authority. |

## Documentation rules

- `MODBUS_MAP.md` records only entries actually present in the BMS protocol document.
- `STATUS_BITS.md` separates read-only runtime-state bits from writable configuration/control bits.
- A bit being readable does **not** authorize its use as a control entity.
- The deployed application remains read-only until a separately reviewed control design explicitly changes that boundary.
- Installation-specific wiring and hardware names remain in protected local configuration/runbooks, not this public/reusable source tree.
