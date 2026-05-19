"""Seedable die abstraction.

A dedicated `Die` class isolates RNG ownership so every `Game` /
`SimulationEngine` run is deterministic given a seed, without leaking
state through the global `random` module.
"""

from __future__ import annotations

import random
from typing import Optional


class Die:
    """A 6-sided die backed by an isolated `random.Random` instance."""

    __slots__ = ("_rng", "sides")

    def __init__(self, seed: Optional[int] = None, sides: int = 6) -> None:
        self.sides = sides
        self._rng = random.Random(seed)

    def roll(self) -> int:
        return self._rng.randint(1, self.sides)

    def reseed(self, seed: Optional[int]) -> None:
        self._rng = random.Random(seed)

    @property
    def rng(self) -> random.Random:
        """Expose the underlying RNG so strategies can share the seed stream."""
        return self._rng
