"""Round-robin tournament: every strategy vs every other strategy.

Results are saved to tournament_results.csv and a heatmap is rendered
showing each strategy's avg final stack when facing each opponent.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from guayabita import GameConfig, PlayerSpec, SimulationEngine
from guayabita.metrics import per_strategy_summary
from guayabita.strategies import (
    AggressiveStrategy,
    ConservativeStrategy,
    MartingaleStrategy,
    ProbabilityStrategy,
    RandomStrategy,
    AllInStrategy,
    ManuelStrategy,
    ManuelStrategy_2,
    BadBunny,
    WilchesStrategy,
    BeltroxStrategy,
    SnowballStrategy,
)

# ---------------------------------------------------------------------------
# Strategy registry – add / remove entries here to change the tournament field
# ---------------------------------------------------------------------------
STRATEGIES: dict[str, object] = {
    "Conservative":  ConservativeStrategy(),
    "Aggressive":    AggressiveStrategy(stack_fraction=0.20),
    "Random":        RandomStrategy(),
    "Martingale":    MartingaleStrategy(base_units=1, max_doublings=5),
    "Probability":   ProbabilityStrategy(max_fraction=0.80, threshold=0.4),
    "AllIn":         AllInStrategy(),
    "Manuel":        ManuelStrategy(),
    "Manuel_2":      ManuelStrategy_2(),
    "BadBunny":      BadBunny(),
    "Wilches":       WilchesStrategy(),
    "Beltrox":       BeltroxStrategy(),
    "Snowball":      SnowballStrategy(),
}

N_GAMES   = 100
SEED      = 18
INITIAL_STACK = 20_000

CONFIG = GameConfig(
    case=500,
    initial_stack=INITIAL_STACK,
    ante_units=1,
    max_rounds=500,
    seed=SEED,
)


def run_tournament() -> pd.DataFrame:
    """Return a DataFrame with one row per matchup containing both players' stats."""
    names = list(STRATEGIES.keys())
    rows: list[dict] = []

    total = len(names) ** 2
    done = 0

    for player_name, player_strat in STRATEGIES.items():
        for opp_name, opp_strat in STRATEGIES.items():
            done += 1
            print(f"[{done:>4}/{total}] {player_name:>15} vs {opp_name:<15}", end="\r")

            specs = [
                PlayerSpec(1, player_strat),
                PlayerSpec(2, opp_strat),
            ]
            engine = SimulationEngine(specs, CONFIG, master_seed=SEED)
            sim = engine.run(n_games=N_GAMES, progress=False)
            summary = per_strategy_summary(sim)

            # Extract stats for both sides (keys are "P1:<strat>" and "P2:<strat>")
            p_key = next(k for k in summary if k.startswith("P1:"))
            o_key = next(k for k in summary if k.startswith("P2:"))

            p_stats = summary[p_key]
            o_stats = summary[o_key]
            game_stats = summary.get("__game__", {})

            rows.append({
                "player":              player_name,
                "opponent":            opp_name,
                "player_avg_final":    p_stats["avg_final_stack"],
                "player_win_rate":     p_stats["win_rate"],
                "player_survival":     p_stats["survival_rate"],
                "opponent_avg_final":  o_stats["avg_final_stack"],
                "opponent_win_rate":   o_stats["win_rate"],
                "opponent_survival":   o_stats["survival_rate"],
                "avg_duration":        game_stats.get("avg_duration", 0.0),
                "draw_rate":           game_stats.get("draw_rate", 0.0),
            })

    print()  # newline after progress
    return pd.DataFrame(rows)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows → {path}")


def build_matrix(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Pivot into a strategy × strategy matrix, rows sorted by row-mean descending."""
    matrix = df.pivot(index="player", columns="opponent", values=value_col)
    row_order = matrix.mean(axis=1).sort_values(ascending=False).index
    return matrix.loc[row_order]


def plot_heatmap(
    matrix: pd.DataFrame,
    title: str,
    fmt: str = ".0f",
    output_path: Path | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(14, 10))

    sns.heatmap(
        matrix,
        annot=True,
        fmt=fmt,
        cmap="RdYlGn",
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": title},
    )

    ax.set_title(title, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Opponent", fontsize=11)
    ax.set_ylabel("Player (row strategy)", fontsize=11)
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved plot → {output_path}")

    plt.show()


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "tournament_output"
    out_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------
    df = run_tournament()

    # ------------------------------------------------------------------
    # Save raw results
    # ------------------------------------------------------------------
    save_csv(df, out_dir / "tournament_results.csv")

    # ------------------------------------------------------------------
    # Heatmap 1: avg final stack of the row-strategy vs each opponent
    # ------------------------------------------------------------------
    avg_stack_matrix = build_matrix(df, "player_avg_final")
    plot_heatmap(
        avg_stack_matrix,
        title="Avg Final Stack  (row strategy vs column opponent)",
        fmt=".0f",
        output_path=out_dir / "heatmap_avg_final_stack.png",
    )

    # ------------------------------------------------------------------
    # Heatmap 2: win rate of the row-strategy vs each opponent
    # ------------------------------------------------------------------
    win_rate_matrix = build_matrix(df, "player_win_rate")
    plot_heatmap(
        win_rate_matrix,
        title="Win Rate  (row strategy vs column opponent)",
        fmt=".2f",
        output_path=out_dir / "heatmap_win_rate.png",
    )


if __name__ == "__main__":
    main()
