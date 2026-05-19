"""Tiny logging helper.

The original `tools.py` was littered with `print(...)` calls; here we
funnel them through a single `GameLogger` so verbosity can be toggled
per `GameConfig` and so simulations stay quiet by default.
"""

from __future__ import annotations

from typing import Callable, Optional


class GameLogger:
    """Minimal logger: a callable sink + on/off toggle.

    Defaults to `print`, but anything callable accepting a `str` works
    (e.g., `logging.getLogger("guayabita").info`).
    """

    __slots__ = ("enabled", "sink")

    def __init__(self, enabled: bool = False, sink: Optional[Callable[[str], None]] = None) -> None:
        self.enabled = enabled
        self.sink = sink or print

    def log(self, msg: str) -> None:
        if self.enabled:
            self.sink(msg)

    def section(self, title: str, width: int = 60) -> None:
        if not self.enabled:
            return
        self.sink("-" * width)
        self.sink(title)
        self.sink("-" * width)
