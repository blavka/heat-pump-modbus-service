"""Thread-safe hand-off of MQTT commands to the Modbus main loop."""

from __future__ import annotations

from queue import Empty, Queue
from threading import Event
from typing import Callable


class CommandQueue:
    """MQTT callbacks enqueue promptly; serial I/O is executed by the main loop."""

    def __init__(self, handler: Callable[[str, bytes], None]) -> None:
        self._handler = handler
        self._items: Queue[tuple[str, bytes]] = Queue()
        self._wake = Event()

    def enqueue(self, topic: str, payload: bytes) -> None:
        self._items.put((topic, payload))
        self._wake.set()

    def drain(self) -> int:
        handled = 0
        while True:
            try:
                topic, payload = self._items.get_nowait()
            except Empty:
                self._wake.clear()
                return handled
            self._handler(topic, payload)
            handled += 1

    def wait_for_work(self, timeout: float) -> bool:
        return self._wake.wait(timeout)
