from dataclasses import dataclass

import numpy as np


@dataclass
class BeliefUpdate:
    """Update information for Bayesian belief state."""

    comparison_results: list[str]


class BayesianBeliefState:
    """Bayesian belief state for inferring target die value.

    Handles pure Bayesian inference without knowledge of actual values.
    """

    def __init__(self, dice_sides: int = 6):
        """Initialize belief state with uniform prior.

        Args:
            dice_sides: Number of sides on the dice
        """
        self.dice_sides = dice_sides
        # Uniform prior over all possible target values
        self.beliefs = np.ones(dice_sides) / dice_sides
        self.evidence_history: list[BeliefUpdate] = []

    def get_current_beliefs(self) -> np.ndarray:
        """Get current belief distribution over target values.

        Returns:
            Array of probabilities for each possible target value (1 to dice_sides)
        """
        return self.beliefs.copy()

    def get_most_likely_target(self) -> int:
        """Get the most likely target value based on current beliefs.

        Returns:
            Most likely target value (1-indexed)
        """
        return np.argmax(self.beliefs) + 1

    def get_belief_for_target(self, target: int) -> float:
        """Get belief probability for a specific target value.

        Args:
            target: Target value (1 to dice_sides)

        Returns:
            Probability that target is the true value
        """
        if not (1 <= target <= self.dice_sides):
            raise ValueError(f"Target must be between 1 and {self.dice_sides}")
        return self.beliefs[target - 1]

    def update_beliefs(self, evidence: BeliefUpdate) -> None:
        """Update beliefs based on new evidence using Bayes' rule.

        Args:
            evidence: New evidence to incorporate
        """
        self.evidence_history.append(evidence)

        comparison_results = evidence.comparison_results

        # Calculate likelihood for each possible target value
        likelihoods = np.zeros(self.dice_sides)

        for target_idx in range(self.dice_sides):
            target_value = target_idx + 1

            # Calculate P(comparison_results | target_value)
            # This is the joint probability that a dice roll would produce ALL these evidence types
            likelihood = self._calculate_joint_likelihood(
                comparison_results, target_value
            )
            likelihoods[target_idx] = likelihood

        # Apply Bayes' rule: posterior ∝ prior * likelihood
        self.beliefs = self.beliefs * likelihoods

        # Normalize to ensure probabilities sum to 1
        total_belief = np.sum(self.beliefs)
        if total_belief > 0:
            self.beliefs = self.beliefs / total_belief
        else:
            # If all likelihoods are 0 (shouldn't happen with valid evidence),
            # reset to uniform distribution
            self.beliefs = np.ones(self.dice_sides) / self.dice_sides

    def _calculate_joint_likelihood(
        self, comparison_results: list[str], target_value: int
    ) -> float:
        """Calculate P(comparison_results | target_value) for multiple evidence types.

        Args:
            comparison_results: List of evidence results (e.g., ["lower", "half"])
            target_value: Target value to calculate likelihood for

        Returns:
            Joint probability of observing all evidence types given the target
        """
        # For multiple evidence types from a single roll, we need to find
        # the probability that a single dice roll satisfies ALL conditions

        # Count dice rolls that satisfy all evidence conditions
        satisfying_rolls = 0

        for dice_roll in range(1, self.dice_sides + 1):
            satisfies_all = True

            for evidence in comparison_results:
                if (
                    (evidence == "higher" and not (dice_roll > target_value))
                    or (evidence == "lower" and not (dice_roll < target_value))
                    or (evidence == "same" and dice_roll != target_value)
                    or (
                        evidence == "half"
                        and not (
                            target_value % 2 == 0 and dice_roll == target_value // 2
                        )
                    )
                    or (
                        evidence == "double"
                        and not (
                            dice_roll == target_value * 2
                            and dice_roll <= self.dice_sides
                        )
                    )
                ):
                    satisfies_all = False
                    break

            if satisfies_all:
                satisfying_rolls += 1

        return satisfying_rolls / self.dice_sides

    def reset_beliefs(self) -> None:
        """Reset beliefs to uniform prior and clear evidence history."""
        self.beliefs = np.ones(self.dice_sides) / self.dice_sides
        self.evidence_history = []

    def get_entropy(self) -> float:
        """Calculate entropy of current belief distribution.

        Returns:
            Entropy in bits (higher = more uncertain)
        """
        # Avoid log(0) by filtering out zero probabilities
        non_zero_beliefs = self.beliefs[self.beliefs > 0]
        if len(non_zero_beliefs) == 0:
            return 0.0
        return -np.sum(non_zero_beliefs * np.log2(non_zero_beliefs))

    def get_evidence_count(self) -> int:
        """Get number of evidence updates received.

        Returns:
            Number of evidence updates
        """
        return len(self.evidence_history)
