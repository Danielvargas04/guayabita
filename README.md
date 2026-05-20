# Guayabita – Strategy Simulation Framework

A Python simulation framework for **Guayabita**, a Colombian dice betting game. Define pluggable betting strategies, run thousands of head-to-head simulations, and analyse the results with built-in metrics and heatmap visualisations.

---

## Table of Contents

1. [The Game](#the-game)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Package Reference](#package-reference)
   - [GameConfig](#gameconfig)
   - [PlayerSpec](#playerspec)
   - [SimulationEngine](#simulationengine)
   - [Results & Metrics](#results--metrics)
6. [Strategies](#strategies)
7. [Example Scripts](#example-scripts)
8. [Tournament & Heatmaps](#tournament--heatmaps)
9. [Writing a Custom Strategy](#writing-a-custom-strategy)

---

## The Game

Guayabita is a 2-or-more player dice-and-chips game where each player starts with a **stack** of chips; a shared **pool** starts empty.

### Setup
- All active players pay an **ante** (`ante_units × case`) into the pool at the start, and again whenever the pool drains to zero.
- Players who can't afford the ante are **eliminated**.

### Per-turn flow

Each turn a player rolls a six-sided die:

| First roll | Outcome |
|-----------|---------|
| **6** | Player wins `case` chips from the pool |
| **1** | Player loses `case` chips to the pool |
| **2 – 5** | **Betting phase** — strategy chooses a bet (must be a whole multiple of `case`); player rolls again; wins if `second die > first die`, else chips go to pool |

Bets are automatically clamped to the player's stack and the current pool size.

**Win probability by first roll:**

| Roll | P(win) |
|------|--------|
| 2 | 4 / 6 ≈ 0.67 |
| 3 | 3 / 6 = 0.50 |
| 4 | 2 / 6 ≈ 0.33 |
| 5 | 1 / 6 ≈ 0.17 |

### Termination
The game ends when fewer than 2 players remain (**winner**) or `max_rounds` is reached (**draw**).

---

## Project Structure

```
guayabita/
├── guayabita/                  # Core package
│   ├── __init__.py             # Public API
│   ├── config.py               # GameConfig, PlayerSpec
│   ├── dice.py                 # Seedable Die
│   ├── player.py               # Player entity
│   ├── game.py                 # Game engine
│   ├── simulation.py           # SimulationEngine (batch runs)
│   ├── results.py              # Telemetry dataclasses
│   ├── metrics.py              # Aggregation helpers
│   ├── logging_utils.py        # Toggleable GameLogger
│   └── strategies/
│       ├── base.py             # Abstract Strategy, StrategyContext
│       ├── conservative.py
│       ├── aggressive.py
│       ├── random_strategy.py
│       ├── martingale.py
│       ├── probability.py
│       ├── all_in.py
│       ├── manuel.py
│       ├── manuel_2.py
│       ├── BadBunny.py
│       ├── wilches.py
│       ├── beltrox.py
│       └── snowball.py
├── examples/
│   ├── single_game.py          # Run & inspect one verbose game
│   ├── compare_strategies.py   # Head-to-head batch comparison
│   └── tournament.py           # Full round-robin tournament + heatmaps
├── main.py                     # Quick demo (3 strategies, 100 games)
├── plots.py                    # Visualise exported CSV results
└── plot.ipynb                  # Jupyter analysis notebook
```

---

## Installation

The core package uses **stdlib only**. The example scripts and analysis tools require a few extra libraries:

```bash
pip install pandas matplotlib seaborn numpy
```

No packaging manifest is needed — all examples patch `sys.path` to import the local package directly.

---

## Quick Start

```python
from guayabita import GameConfig, PlayerSpec, SimulationEngine
from guayabita.metrics import format_summary, per_strategy_summary
from guayabita.strategies import ConservativeStrategy, AggressiveStrategy

specs = [
    PlayerSpec(1, ConservativeStrategy()),
    PlayerSpec(2, AggressiveStrategy(stack_fraction=0.25)),
]

config = GameConfig(
    case=500,
    initial_stack=20_000,
    ante_units=1,
    max_rounds=5000,
    seed=42,
)

engine = SimulationEngine(specs, config, master_seed=42)
sim = engine.run(n_games=200)

print(format_summary(per_strategy_summary(sim)))
```

---

## Package Reference

### GameConfig

```python
@dataclass(frozen=True)
class GameConfig:
    case: int = 100               # Base chip unit (ante, bets are multiples of this)
    initial_stack: int = 30_000   # Starting stack per player
    ante_units: int = 1           # Ante = ante_units × case
    max_rounds: int = 500         # Hard round cap (draw if reached)
    min_active_stack: int | None = None   # Stack below which a player is eliminated
    allow_pool_overdraw: bool = False     # If False, payouts are capped to pool size
    seed: int | None = None       # RNG seed (None = random)
    verbose: bool = False         # Print turn-by-turn log
```

Helper methods: `ante_amount()`, `effective_min_stack()`.

### PlayerSpec

```python
PlayerSpec(
    player_id,          # Any hashable (int, str, …)
    strategy,           # Strategy instance
    initial_stack=None, # Override GameConfig.initial_stack
    label=None,         # Human-readable name for logs
)
```

### SimulationEngine

```python
engine = SimulationEngine(player_specs, base_config, master_seed=None)
sim    = engine.run(n_games=100, verbose=False, progress=False)
```

- `master_seed` drives deterministic per-game seed generation.
- `progress=True` prints a line counter while running.

### Results & Metrics

| Object | Key attributes |
|--------|---------------|
| `GameResult` | `winner_id`, `rounds_played`, `final_stacks`, `elimination_round`, `pool_evolution`, `stack_evolution`, `invariant_ok` |
| `SimulationResult` | `n_games`, `game_results`, `strategy_by_player` |

**Metric helpers** (`guayabita.metrics`):

| Function | Returns |
|----------|---------|
| `per_strategy_summary(sim)` | Dict of win rate, survival rate, avg/median/std final stack per player slot |
| `format_summary(summary)` | ASCII table string for CLI output |
| `average_pool_evolution(sim)` | `List[float]` — mean pool at each round |
| `average_stack_evolution(sim)` | `List[float]` — mean stack at each round |
| `stack_evolution(sim)` | Raw per-game stack time series |
| `pool_evolution(sim)` | Raw per-game pool time series |

---

## Strategies

| Name | Class | Behaviour |
|------|-------|-----------|
| `conservative` | `ConservativeStrategy` | Bets the minimum (`case × multiplier`, default 1×) every turn |
| `aggressive` | `AggressiveStrategy` | Bets a fixed fraction of its current stack (default 25%) |
| `random` | `RandomStrategy` | Picks a uniform random bet between `case` and the pool |
| `martingale` | `MartingaleStrategy` | Doubles the bet after each loss (up to `max_doublings`), resets on win |
| `probability` | `ProbabilityStrategy` | Scales bet by P(win) for the first roll; bets minimum when below `threshold` |
| `all_in` | `AllInStrategy` | Bets the entire pool |
| `manuel` | `ManuelStrategy` | Bets the pool on roll 2; otherwise bets `case` |
| `manuel_2` | `ManuelStrategy_2` | Bets the pool on rolls 2 or 3; otherwise bets `case` |
| `bad_bunny` | `BadBunny` | When pool < stack: bets pool on 2/3; when pool ≥ stack: bets pool/3 on roll 2; otherwise `case` |
| `wilches` | `WilchesStrategy` | Roll-dependent tiers: pool on 2; pool or stack fractions on 3/4; `case` on 5 |
| `beltrox` | `BeltroxStrategy` | Probability-weighted fractions of pool/stack depending on roll |
| `snowball` | `SnowballStrategy` | Two modes — "winner" (aggressive fractions) when ahead of `initial_stack`, "loser" (all-in on 2) when behind |

Strategies implement the abstract interface from `guayabita.strategies.base`:

```python
class Strategy:
    def decide_bet(self, context: StrategyContext) -> int: ...
    def observe(self, outcome: BetOutcome) -> None: ...   # called after bet resolves
    def reset(self) -> None: ...                          # called between games
```

`StrategyContext` exposes: `round`, `stack`, `pool`, `first_roll`, `rng`, `bet_history`.

---

## Example Scripts

### `examples/single_game.py`
Runs a single verbose game and prints a turn-by-turn log. Optionally exports `stack_evolution` and `pool_evolution` to `results.csv`.

```bash
python examples/single_game.py
python examples/single_game.py --export   # saves results.csv
```

### `examples/compare_strategies.py`
Runs 100 games between two or more strategies and prints a summary table. Supports CSV export of all game series.

```bash
python examples/compare_strategies.py
python examples/compare_strategies.py --export   # saves results/game_*.csv
```

### `examples/tournament.py`
Full round-robin tournament (see next section).

---

## Tournament & Heatmaps

`examples/tournament.py` runs every registered strategy against every other strategy (144 matchups for 12 strategies), 100 games each.

```bash
python examples/tournament.py
```

Outputs are written to `tournament_output/`:

| File | Contents |
|------|---------|
| `tournament_results.csv` | Long-form table — one row per matchup with both players' avg final stack, win rate, survival rate, avg game duration, and draw rate |
| `heatmap_avg_final_stack.png` | 12 × 12 heatmap — row strategy's **avg final stack** vs each column opponent; rows sorted by row-mean descending |
| `heatmap_win_rate.png` | Same layout showing **win rate** |

To change the field, edit the `STRATEGIES` dict or `N_GAMES` constant at the top of `tournament.py`.

---

## Writing a Custom Strategy

1. Create a new file under `guayabita/strategies/`.
2. Subclass `Strategy` and implement `decide_bet`:

```python
from guayabita.strategies.base import Strategy, StrategyContext

class MyStrategy(Strategy):
    name = "my_strategy"

    def decide_bet(self, context: StrategyContext) -> int:
        # context.first_roll  — the roll that triggered the betting phase (2–5)
        # context.stack       — your current chip count
        # context.pool        — current shared pool
        # context.round       — current round index
        # Return a positive integer; engine snaps it to the nearest case multiple
        # and clamps to min(stack, pool).
        return context.pool // 2
```

3. Register it in `guayabita/strategies/__init__.py` and add a `PlayerSpec` in your script.
