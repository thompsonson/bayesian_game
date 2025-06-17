from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..belief.belief_domain import BayesianBeliefState, BeliefUpdate
from ..environment.environment_domain import (
    Environment,
    EnvironmentEvidence,
    EvidenceType,
)


class GamePhase(Enum):
    """Phases of the Bayesian Game."""

    SETUP = "setup"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class GameState:
    """Current state of the Bayesian Game."""

    round_number: int
    max_rounds: int
    phase: GamePhase
    target_value: int = None
    evidence_history: list[EnvironmentEvidence] = None
    current_beliefs: list[float] = None
    most_likely_target: int = None
    belief_entropy: float = None

    def __post_init__(self):
        if self.evidence_history is None:
            self.evidence_history = []
        if self.current_beliefs is None:
            self.current_beliefs = []


class BayesianGame:
    """Main orchestration class for the Bayesian Game.

    Coordinates between Environment and Belief domains while maintaining
    clean separation of concerns.
    """

    def __init__(
        self,
        dice_sides: int = 6,
        max_rounds: int = 10,
        evidence_type: EvidenceType = EvidenceType.BASIC,
        seed: int | None = None,
    ):
        """Initialize the Bayesian Game.

        Args:
            dice_sides: Number of sides on the dice
            max_rounds: Maximum number of rounds to play
            evidence_type: Type of evidence to generate (basic or extended)
            seed: Random seed for reproducible results
        """
        self.dice_sides = dice_sides
        self.max_rounds = max_rounds
        self.evidence_type = evidence_type

        # Initialize domains
        self.environment = Environment(
            dice_sides=dice_sides, evidence_type=evidence_type, seed=seed
        )
        self.belief_state = BayesianBeliefState(dice_sides=dice_sides)

        # Initialize game state
        self.game_state = GameState(
            round_number=0, max_rounds=max_rounds, phase=GamePhase.SETUP
        )

    def start_new_game(self, target_value: int | None = None) -> GameState:
        """Start a new game with optional specific target value.

        Args:
            target_value: Specific target value, or None for random

        Returns:
            Initial game state
        """
        # Reset domains
        self.belief_state.reset_beliefs()

        # Set target value
        if target_value is not None:
            self.environment.set_target_value(target_value)
        else:
            self.environment.generate_random_target()

        # Reset game state
        self.game_state = GameState(
            round_number=0,
            max_rounds=self.max_rounds,
            phase=GamePhase.PLAYING,
            target_value=self.environment.get_target_value(),
            evidence_history=[],
            current_beliefs=self.belief_state.get_current_beliefs().tolist(),
            most_likely_target=self.belief_state.get_most_likely_target(),
            belief_entropy=self.belief_state.get_entropy(),
        )

        return self.game_state

    def play_round(self) -> GameState:
        """Play one round of the game.

        Returns:
            Updated game state after the round

        Raises:
            ValueError: If game is not in playing phase
        """
        if self.game_state.phase != GamePhase.PLAYING:
            raise ValueError("Game is not in playing phase")

        if self.game_state.round_number >= self.max_rounds:
            raise ValueError("Game has already finished")

        # Generate evidence from environment
        evidence = self.environment.roll_dice_and_compare()

        # Update belief state (only pass comparison results, not dice roll)
        belief_update = BeliefUpdate(comparison_results=evidence.comparison_results)
        self.belief_state.update_beliefs(belief_update)

        # Update game state
        self.game_state.round_number += 1
        self.game_state.evidence_history.append(evidence)
        self.game_state.current_beliefs = (
            self.belief_state.get_current_beliefs().tolist()
        )
        self.game_state.most_likely_target = self.belief_state.get_most_likely_target()
        self.game_state.belief_entropy = self.belief_state.get_entropy()

        # Check if game is finished
        if self.game_state.round_number >= self.max_rounds:
            self.game_state.phase = GamePhase.FINISHED

        return self.game_state

    def get_current_state(self) -> GameState:
        """Get current game state.

        Returns:
            Current game state
        """
        return self.game_state

    def is_game_finished(self) -> bool:
        """Check if game is finished.

        Returns:
            True if game is finished
        """
        return self.game_state.phase == GamePhase.FINISHED

    def get_final_guess_accuracy(self) -> float:
        """Get accuracy of final guess (belief for true target).

        Returns:
            Probability assigned to true target value

        Raises:
            ValueError: If target value is not set
        """
        if self.game_state.target_value is None:
            raise ValueError("Target value not set")

        return self.belief_state.get_belief_for_target(self.game_state.target_value)

    def was_final_guess_correct(self) -> bool:
        """Check if the most likely target matches the true target.

        Returns:
            True if most likely target equals true target

        Raises:
            ValueError: If target value is not set
        """
        if self.game_state.target_value is None:
            raise ValueError("Target value not set")

        return bool(self.game_state.most_likely_target == self.game_state.target_value)

    def get_game_summary(self) -> dict[str, Any]:
        """Get summary of completed game.

        Returns:
            Dictionary with game summary statistics
        """
        return {
            "rounds_played": self.game_state.round_number,
            "max_rounds": self.max_rounds,
            "true_target": self.game_state.target_value,
            "final_guess": self.game_state.most_likely_target,
            "guess_correct": self.was_final_guess_correct(),
            "final_accuracy": self.get_final_guess_accuracy(),
            "final_entropy": self.game_state.belief_entropy,
            "evidence_count": len(self.game_state.evidence_history),
            "final_beliefs": dict(enumerate(self.game_state.current_beliefs, 1)),
        }
