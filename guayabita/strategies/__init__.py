"""Strategy registry.

Adding a new strategy:
    1. Subclass `Strategy` from `guayabita.strategies.base`.
    2. Implement `decide_bet(context) -> int`.
    3. (Optional) override `observe(...)` to keep internal state.
    4. Import + add to `STRATEGIES` below if you want CLI / registry access.
"""

from .base import Strategy, StrategyContext, BetOutcome
from .conservative import ConservativeStrategy
from .aggressive import AggressiveStrategy
from .random_strategy import RandomStrategy
from .martingale import MartingaleStrategy
from .probability import ProbabilityStrategy
from .all_in import AllInStrategy
from .manuel import ManuelStrategy
from .manuel_2 import ManuelStrategy_2
from .BadBunny import BadBunny
from .wilches import WilchesStrategy
from .beltrox import BeltroxStrategy
from .snowball import SnowballStrategy
STRATEGIES = {
    "conservative": ConservativeStrategy,
    "aggressive": AggressiveStrategy,
    "random": RandomStrategy,
    "martingale": MartingaleStrategy,
    "probability": ProbabilityStrategy,
    "all_in": AllInStrategy,
    "manuel": ManuelStrategy,
    "manuel_2": ManuelStrategy_2,
    "bad_bunny": BadBunny,
    "wilches": WilchesStrategy,
    "beltrox": BeltroxStrategy,
    "snowball": SnowballStrategy,
}

__all__ = [
    "Strategy",
    "StrategyContext",
    "BetOutcome",
    "ConservativeStrategy",
    "AggressiveStrategy",
    "RandomStrategy",
    "MartingaleStrategy",
    "ProbabilityStrategy",
    "AllInStrategy",
    "ManuelStrategy",
    "ManuelStrategy_2",
    "BadBunny",
    "WilchesStrategy",
    "BeltroxStrategy",
    "SnowballStrategy",
]
