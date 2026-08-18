"""Suppress insignificant temperature changes while retaining current state."""

from __future__ import annotations

from collections.abc import Mapping


class TelemetryFilter:
    """UniPi-compatible delta filter: retain the first value and changes >= threshold."""

    def __init__(self, *, temperature_names: set[str], temperature_diff: float) -> None:
        self.temperature_names = temperature_names
        self.temperature_diff = temperature_diff
        self._last_temperatures: dict[str, float] = {}

    def values_to_publish(self, values: Mapping[str, object]) -> dict[str, object]:
        result: dict[str, object] = {}
        for name, value in values.items():
            if name not in self.temperature_names or not isinstance(value, (int, float)):
                result[name] = value
                continue
            previous = self._last_temperatures.get(name)
            if previous is not None and abs(value - previous) < self.temperature_diff:
                continue
            result[name] = value
            self._last_temperatures[name] = float(value)
        return result
