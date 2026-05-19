"""Single-game engine.

Pool funding:
    The pool always starts empty. Each active player antes
    `config.ante_amount()` (= ante_units * case) to seed it. The same
    ante is collected again, dynamically, every time the pool drains
    to 0 mid-game. Players who cannot afford an ante are eliminated
    on the spot.

Game flow per round:
    for each active player (in seated order):
        0. if pool is empty, collect a fresh ante from active players
        1. roll first die
            - 6  -> player wins `case` from pool
            - 1  -> player loses `case` to pool
            - 2..5 -> "action": strategy chooses bet, roll second die
                        * second > first -> player wins bet (pool pays bet)
                        * else            -> player loses bet (pool keeps it)
        2. clamp transfers to available pool / stack
        3. mark player inactive if stack < min_active_stack
    end-of-round: snapshot, check invariant, check termination

Termination:
    * fewer than 2 active players, OR
    * round_index >= config.max_rounds.

Money is strictly conserved (pool + sum(stacks) == initial_total)
when `allow_pool_overdraw` is False, which we verify per round.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from .config import GameConfig, PlayerSpec
from .dice import Die
from .logging_utils import GameLogger
from .player import Player
from .results import GameResult, RoundSnapshot, TurnOutcome
from .strategies.base import BetOutcome, StrategyContext


class Game:
    def __init__(
        self,
        player_specs: Sequence[PlayerSpec],
        config: GameConfig,
        logger: Optional[GameLogger] = None,
    ) -> None:
        if len(player_specs) < 2:
            raise ValueError("Guayabita requires at least 2 players.")
        self.config = config
        self.logger = logger or GameLogger(enabled=config.verbose)
        self.die = Die(seed=config.seed)

        self.players: List[Player] = []
        for spec in player_specs:
            spec.strategy.reset()
            self.players.append(
                Player(
                    id=spec.player_id,
                    stack=spec.initial_stack if spec.initial_stack is not None else config.initial_stack,
                    strategy=spec.strategy,
                )
            )
        self.pool: int = 0
        self.round_index: int = 0
        self.snapshots: List[RoundSnapshot] = []
        self.ante_events: List[tuple[int, int, List[int]]] = []
        self._initial_total = sum(p.stack for p in self.players)
        self._collect_ante(reason="initial")

    # ----- helpers ---------------------------------------------------------

    def _active(self) -> List[Player]:
        return [p for p in self.players if p.active]

    def _update_active(self) -> None:
        min_stack = self.config.effective_min_stack()
        for p in self.players:
            if p.active and p.stack < min_stack:
                p.deactivate(self.round_index)
                self.logger.log(f"  >> Player {p.id} eliminated (stack={p.stack})")

    def _transfer_from_pool(self, amount: int) -> int:
        """Move up to `amount` out of the pool. Returns the actual amount paid."""
        if self.config.allow_pool_overdraw:
            paid = amount
        else:
            paid = min(amount, self.pool)
        self.pool -= paid
        return paid

    def _collect_ante(self, reason: str) -> int:
        """Each active player contributes `config.ante_amount()` to the pool.

        Players who cannot afford the ante are eliminated (they do not
        contribute). Returns the total amount added to the pool.
        Conservation is preserved: money only moves stack -> pool.
        """
        ante = self.config.ante_amount()
        if ante <= 0:
            return 0
        contributors: List[int] = []
        total = 0
        for p in self.players:
            if not p.active:
                continue
            if p.stack < ante:
                p.deactivate(self.round_index)
                self.logger.log(f"  >> P{p.id} cannot afford ante ({ante}), eliminated")
                continue
            p.stack -= ante
            self.pool += ante
            total += ante
            contributors.append(p.id)
        self.ante_events.append((self.round_index, ante, contributors))
        self.logger.log(
            f"  ante ({reason}): {len(contributors)} players x {ante} -> pool={self.pool}"
        )
        return total

    def _ensure_pool_funded(self) -> None:
        """Refill the pool from active players if it has drained to 0."""
        if self.pool <= 0 and len(self._active()) >= 2:
            self._collect_ante(reason=f"refill@round{self.round_index}")

    # ----- core mechanics --------------------------------------------------

    def play_turn(self, player: Player) -> TurnOutcome:
        cfg = self.config
        first_roll = self.die.roll()
        stack_before, pool_before = player.stack, self.pool

        if first_roll == 6:
            paid = self._transfer_from_pool(cfg.case)
            player.stack += paid
            outcome = TurnOutcome(
                self.round_index, player.id, first_roll, None,
                "win6", 0, +paid, -paid, player.stack, self.pool,
            )
            self.logger.log(f"  P{player.id} rolls {first_roll} -> wins {paid} (stack={player.stack}, pool={self.pool})")
            return outcome

        if first_roll == 1:
            loss = min(cfg.case, player.stack)
            player.stack -= loss
            self.pool += loss
            outcome = TurnOutcome(
                self.round_index, player.id, first_roll, None,
                "lose1", 0, -loss, +loss, player.stack, self.pool,
            )
            self.logger.log(f"  P{player.id} rolls {first_roll} -> loses {loss} (stack={player.stack}, pool={self.pool})")
            return outcome

        # Action phase (rolls 2..5).
        ctx = StrategyContext(
            round_index=self.round_index,
            player_id=player.id,
            player_stack=player.stack,
            pool=self.pool,
            case=cfg.case,
            first_roll=first_roll,
            rng=self.die.rng,
            own_history=list(player.strategy.history),
        )
        requested = max(0, int(player.decide_bet(ctx)))
        bet = min(requested, player.stack, self.pool if not cfg.allow_pool_overdraw else requested)
        bet = (bet // cfg.case) * cfg.case  # enforce multiple-of-case post-clamp

        if bet <= 0:
            self.logger.log(f"  P{player.id} rolls {first_roll} -> action but bets 0 (pass)")
            return TurnOutcome(
                self.round_index, player.id, first_roll, None,
                "pass", 0, 0, 0, player.stack, self.pool,
            )

        # Stake leaves the player and enters the pool until resolution.
        player.stack -= bet
        self.pool += bet

        second_roll = self.die.roll()
        won = second_roll > first_roll
        if won:
            paid = self._transfer_from_pool(2 * bet)
            player.stack += paid
        # else: stake remains in pool (already moved).

        player.strategy.observe(
            BetOutcome(self.round_index, first_roll, second_roll, bet, won)
        )

        action = "bet_win" if won else "bet_lose"
        self.logger.log(
            f"  P{player.id} rolls {first_roll} -> bets {bet}, second={second_roll} "
            f"-> {'WIN' if won else 'LOSE'} (stack={player.stack}, pool={self.pool})"
        )
        return TurnOutcome(
            self.round_index, player.id, first_roll, second_roll,
            action, bet,
            player.stack - stack_before, self.pool - pool_before,
            player.stack, self.pool,
        )

    def play_round(self) -> RoundSnapshot:
        self.round_index += 1
        self.logger.section(f"Round {self.round_index}")
        snap = RoundSnapshot(
            round_index=self.round_index,
            pool=self.pool,
            stacks={p.id: p.stack for p in self.players},
            active_players=[p.id for p in self._active()],
        )
        for player in list(self._active()):
            self._ensure_pool_funded()
            if not player.active:
                continue
            if len(self._active()) < 2:
                break
            snap.turns.append(self.play_turn(player))
        self._update_active()
        for p in self.players:
            p.record_stack()
        snap.pool = self.pool
        snap.stacks = {p.id: p.stack for p in self.players}
        snap.active_players = [p.id for p in self._active()]
        self.snapshots.append(snap)
        self._assert_invariant()
        return snap

    def run(self) -> GameResult:
        cfg = self.config
        while len(self._active()) >= 2 and self.round_index < cfg.max_rounds:
            self.play_round()

        active = self._active()
        winner_id = active[0].id if len(active) == 1 else None

        final_total = self.pool + sum(p.stack for p in self.players)
        result = GameResult(
            seed=cfg.seed,
            rounds_played=self.round_index,
            winner_id=winner_id,
            final_pool=self.pool,
            final_stacks={p.id: p.stack for p in self.players},
            strategy_by_player={p.id: p.strategy.name for p in self.players},
            elimination_round={p.id: p.eliminated_round for p in self.players},
            pool_evolution=[s.pool for s in self.snapshots],
            stack_evolution={p.id: list(p.stack_history) for p in self.players},
            invariant_ok=(final_total == self._initial_total) or cfg.allow_pool_overdraw,
            initial_total_money=self._initial_total,
            final_total_money=final_total,
        )

        if self.logger.enabled:
            self.logger.section("Game over")
            self.logger.log(f"Rounds played: {result.rounds_played}")
            self.logger.log(f"Winner: {result.winner_id}")
            self.logger.log(f"Final pool: {result.final_pool}")
            self.logger.log(f"Final stacks: {result.final_stacks}")
            self.logger.log(f"Invariant OK: {result.invariant_ok}")
        return result

    # ----- safety ----------------------------------------------------------

    def _assert_invariant(self) -> None:
        if self.config.allow_pool_overdraw:
            return
        total = self.pool + sum(p.stack for p in self.players)
        if total != self._initial_total:  # pragma: no cover - defensive
            raise RuntimeError(
                f"Accounting invariant broken at round {self.round_index}: "
                f"expected {self._initial_total}, got {total}"
            )
