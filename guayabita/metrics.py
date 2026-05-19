"""Aggregate metrics over `SimulationResult` objects.

All metrics are returned as plain dicts of native python types so the
output is trivially serializable / convertible to pandas later on.
"""

from __future__ import annotations

from statistics import mean, median, pstdev
from typing import Dict, List

from .results import SimulationResult


def _safe_mean(xs: List[float]) -> float:
    return float(mean(xs)) if xs else 0.0


def _safe_pstdev(xs: List[float]) -> float:
    return float(pstdev(xs)) if len(xs) > 1 else 0.0


def per_strategy_summary(sim: SimulationResult) -> Dict[str, Dict[str, float]]:
    """Win rate, survival rate, final-stack stats per *player slot*.

    Keyed by `"P{id}:{strategy}"` to remain unambiguous when two
    players share a strategy class but with different parameters.
    """
    finals = sim.final_stacks_by_player()
    n = sim.n_games
    summary: Dict[str, Dict[str, float]] = {}

    wins: Dict[int, int] = {pid: 0 for pid in sim.strategy_by_player}
    survivals: Dict[int, int] = {pid: 0 for pid in sim.strategy_by_player}
    durations: List[int] = []

    for g in sim.game_results:
        durations.append(g.rounds_played)
        if g.winner_id is not None:
            wins[g.winner_id] += 1
        for pid, elim in g.elimination_round.items():
            if elim == -1:
                survivals[pid] += 1

    for pid, strat in sim.strategy_by_player.items():
        stacks = finals.get(pid, [])
        summary[f"P{pid}:{strat}"] = {
            "games": float(n),
            "wins": float(wins[pid]),
            "win_rate": wins[pid] / n if n else 0.0,
            "survival_rate": survivals[pid] / n if n else 0.0,
            "avg_final_stack": _safe_mean(stacks),
            "median_final_stack": float(median(stacks)) if stacks else 0.0,
            "std_final_stack": _safe_pstdev(stacks),
            "min_final_stack": float(min(stacks)) if stacks else 0.0,
            "max_final_stack": float(max(stacks)) if stacks else 0.0,
        }

    summary["__game__"] = {
        "avg_duration": _safe_mean([float(d) for d in durations]),
        "median_duration": float(median(durations)) if durations else 0.0,
        "draw_rate": sum(1 for g in sim.game_results if g.winner_id is None) / n if n else 0.0,
        "invariant_failures": float(sum(1 for g in sim.game_results if not g.invariant_ok)),
    }
    return summary


def average_pool_evolution(sim: SimulationResult) -> List[float]:
    """Mean pool size at round t, truncated to the shortest game."""
    if not sim.game_results:
        return []
    min_len = min(len(g.pool_evolution) for g in sim.game_results)
    if min_len == 0:
        return []
    return [
        _safe_mean([float(g.pool_evolution[t]) for g in sim.game_results])
        for t in range(min_len)
    ]


def format_summary(summary: Dict[str, Dict[str, float]]) -> str:
    """Pretty plain-text table for CLI inspection."""
    lines = []
    header = f"{'slot':<24} {'win_rate':>9} {'survival':>9} {'avg_final':>12} {'std_final':>12}"
    lines.append(header)
    lines.append("-" * len(header))
    for slot, stats in summary.items():
        if slot == "__game__":
            continue
        lines.append(
            f"{slot:<24} {stats['win_rate']:>9.3f} {stats['survival_rate']:>9.3f} "
            f"{stats['avg_final_stack']:>12.1f} {stats['std_final_stack']:>12.1f}"
        )
    if "__game__" in summary:
        g = summary["__game__"]
        lines.append("")
        lines.append(
            f"avg_duration={g['avg_duration']:.2f}  draw_rate={g['draw_rate']:.3f}  "
            f"invariant_failures={int(g['invariant_failures'])}"
        )
    return "\n".join(lines)
