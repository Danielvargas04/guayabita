from __future__ import annotations

from .base import BetOutcome, Strategy, StrategyContext


class MartingaleStrategy(Strategy):
    """Double the bet after every loss; reset to base on win.

    Includes a `max_doublings` safety cap so a long losing streak does
    not request astronomical bets (the engine would clamp them anyway,
    but capping internally keeps the state coherent).
    """

    name = "martingale"

    def __init__(self, base_units: int = 1, max_doublings: int = 6) -> None:
        super().__init__()
        self.base_units = max(1, base_units)
        self.max_doublings = max(0, max_doublings)
        self._streak = 0

    def reset(self) -> None:
        super().reset()
        self._streak = 0

    def observe(self, outcome: BetOutcome) -> None:
        super().observe(outcome)
        if outcome.won:
            self._streak = 0
        else:
            self._streak = min(self._streak + 1, self.max_doublings)

    def decide_bet(self, context: StrategyContext) -> int:
        return self.base_units * context.case * (2 ** self._streak)
