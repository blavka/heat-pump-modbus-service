"""Selection of telemetry that should be visible to MQTT and Home Assistant."""

from collections.abc import Iterable, Mapping


def included_values(values: Mapping[str, object], excluded: Iterable[str]) -> dict[str, object]:
    excluded_names = set(excluded)
    return {name: value for name, value in values.items() if name not in excluded_names}
