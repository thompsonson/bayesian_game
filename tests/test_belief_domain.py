import numpy as np
import pytest

from domains.belief.belief_domain import BayesianBeliefState, BeliefUpdate


class TestBeliefUpdate:
    """Test the BeliefUpdate dataclass."""

    def test_belief_update_creation(self):
        """Test creating belief update with valid data."""
        update = BeliefUpdate(comparison_results=["higher"])
        assert update.comparison_results == ["higher"]

    def test_belief_update_all_results(self):
        """Test belief update with all comparison results."""
        valid_results = ["higher", "lower", "same"]
        for result in valid_results:
            update = BeliefUpdate(comparison_results=[result])
            assert update.comparison_results == [result]


class TestBayesianBeliefState:
    """Test the BayesianBeliefState class."""

    def test_initialization_default(self):
        """Test initialization with default parameters."""
        belief_state = BayesianBeliefState()

        assert belief_state.dice_sides == 6
        assert len(belief_state.beliefs) == 6
        assert np.allclose(belief_state.beliefs, 1 / 6)  # Uniform prior
        assert len(belief_state.evidence_history) == 0

    def test_initialization_custom(self):
        """Test initialization with custom dice sides."""
        belief_state = BayesianBeliefState(dice_sides=8)

        assert belief_state.dice_sides == 8
        assert len(belief_state.beliefs) == 8
        assert np.allclose(belief_state.beliefs, 1 / 8)  # Uniform prior

    def test_get_current_beliefs(self):
        """Test getting current beliefs returns copy."""
        belief_state = BayesianBeliefState(dice_sides=6)
        beliefs = belief_state.get_current_beliefs()

        # Should be a copy, not reference
        beliefs[0] = 0.5
        assert not np.array_equal(beliefs, belief_state.beliefs)
        assert np.allclose(belief_state.beliefs, 1 / 6)

    def test_get_most_likely_target_uniform(self):
        """Test getting most likely target with uniform distribution."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # With uniform distribution, should return first target (index 0 + 1)
        most_likely = belief_state.get_most_likely_target()
        assert most_likely == 1

    def test_get_most_likely_target_after_update(self):
        """Test getting most likely target after belief update."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Update with evidence that favors lower target values
        update = BeliefUpdate(comparison_results=["higher"])
        belief_state.update_beliefs(update)

        # Lower targets are more likely to result in "higher" comparison
        most_likely = belief_state.get_most_likely_target()
        assert most_likely in range(1, 7)  # Should be valid

    def test_get_belief_for_target_valid(self):
        """Test getting belief for valid target values."""
        belief_state = BayesianBeliefState(dice_sides=6)

        for target in range(1, 7):
            belief = belief_state.get_belief_for_target(target)
            assert abs(belief - 1 / 6) < 1e-10  # Should be uniform initially

    def test_get_belief_for_target_invalid(self):
        """Test getting belief for invalid target values raises error."""
        belief_state = BayesianBeliefState(dice_sides=6)

        invalid_targets = [0, 7, -1, 10]
        for target in invalid_targets:
            with pytest.raises(ValueError, match="Target must be between 1 and 6"):
                belief_state.get_belief_for_target(target)

    def test_update_beliefs_higher(self):
        """Test belief update with 'higher' evidence."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Evidence: comparison result is "higher" (dice roll > target)
        # This is more likely for lower target values
        update = BeliefUpdate(comparison_results=["higher"])
        belief_state.update_beliefs(update)

        # Lower targets should have higher probability than higher targets
        # Target 1: P(roll > 1) = 5/6
        # Target 6: P(roll > 6) = 0/6
        prob_1 = belief_state.get_belief_for_target(1)
        prob_6 = belief_state.get_belief_for_target(6)

        assert prob_1 > prob_6  # Target 1 should be more likely than target 6
        assert abs(prob_6 - 0.0) < 1e-10  # Target 6 should have zero probability

    def test_update_beliefs_lower(self):
        """Test belief update with 'lower' evidence."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Evidence: comparison result is "lower" (dice roll < target)
        # This is more likely for higher target values
        update = BeliefUpdate(comparison_results=["lower"])
        belief_state.update_beliefs(update)

        # Higher targets should have higher probability than lower targets
        # Target 1: P(roll < 1) = 0/6
        # Target 6: P(roll < 6) = 5/6
        prob_1 = belief_state.get_belief_for_target(1)
        prob_6 = belief_state.get_belief_for_target(6)

        assert prob_6 > prob_1  # Target 6 should be more likely than target 1
        assert abs(prob_1 - 0.0) < 1e-10  # Target 1 should have zero probability

    def test_update_beliefs_same(self):
        """Test belief update with 'same' evidence."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Evidence: comparison result is "same" (dice roll = target)
        # This has equal probability for all targets: P(roll = target) = 1/6
        update = BeliefUpdate(comparison_results=["same"])
        belief_state.update_beliefs(update)

        # All targets should have equal probability since P(roll = target) = 1/6 for all
        for target in range(1, 7):
            prob = belief_state.get_belief_for_target(target)
            assert abs(prob - 1 / 6) < 1e-10  # Should remain uniform

    def test_update_beliefs_multiple(self):
        """Test multiple belief updates."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # First update: "higher" (favors lower targets)
        update1 = BeliefUpdate(comparison_results=["higher"])
        belief_state.update_beliefs(update1)

        # Second update: "lower" (favors higher targets)
        update2 = BeliefUpdate(comparison_results=["lower"])
        belief_state.update_beliefs(update2)

        # The combination should favor middle targets
        # Target 1: P(roll>1) * P(roll<1) = 5/6 * 0 = 0
        # Target 6: P(roll>6) * P(roll<6) = 0 * 5/6 = 0
        # Middle targets should have non-zero probability

        prob_1 = belief_state.get_belief_for_target(1)
        prob_6 = belief_state.get_belief_for_target(6)
        prob_3 = belief_state.get_belief_for_target(3)

        assert abs(prob_1 - 0.0) < 1e-10  # Target 1 should be eliminated
        assert abs(prob_6 - 0.0) < 1e-10  # Target 6 should be eliminated
        assert prob_3 > 0  # Middle targets should have some probability

    def test_update_beliefs_evidence_history(self):
        """Test that evidence history is maintained."""
        belief_state = BayesianBeliefState(dice_sides=6)

        updates = [
            BeliefUpdate(comparison_results=["higher"]),
            BeliefUpdate(comparison_results=["lower"]),
            BeliefUpdate(comparison_results=["same"]),
        ]

        for update in updates:
            belief_state.update_beliefs(update)

        assert len(belief_state.evidence_history) == 3
        assert belief_state.evidence_history == updates

    def test_reset_beliefs(self):
        """Test resetting beliefs to uniform prior."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Update beliefs
        update = BeliefUpdate(comparison_results=["higher"])
        belief_state.update_beliefs(update)

        # Verify beliefs changed from uniform
        prob_1 = belief_state.get_belief_for_target(1)
        prob_6 = belief_state.get_belief_for_target(6)
        assert prob_1 != prob_6  # Should no longer be uniform
        assert len(belief_state.evidence_history) == 1

        # Reset beliefs
        belief_state.reset_beliefs()

        # Should be back to uniform
        for target in range(1, 7):
            assert abs(belief_state.get_belief_for_target(target) - 1 / 6) < 1e-10
        assert len(belief_state.evidence_history) == 0

    def test_get_entropy_uniform(self):
        """Test entropy calculation for uniform distribution."""
        belief_state = BayesianBeliefState(dice_sides=6)

        entropy = belief_state.get_entropy()
        expected_entropy = np.log2(6)  # Maximum entropy for 6 outcomes
        assert abs(entropy - expected_entropy) < 1e-10

    def test_get_entropy_certain(self):
        """Test entropy calculation for certain distribution."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Create a near-certain belief by applying many "higher" updates
        # This will eventually make target 1 much more likely than others
        for _ in range(10):
            update = BeliefUpdate(comparison_results=["higher"])
            belief_state.update_beliefs(update)

        entropy = belief_state.get_entropy()
        max_entropy = np.log2(6)
        assert entropy < max_entropy  # Should be much less than maximum entropy

    def test_get_entropy_partial(self):
        """Test entropy calculation for partial certainty."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Reduce uncertainty but don't eliminate it
        update = BeliefUpdate(comparison_results=["higher"])
        belief_state.update_beliefs(update)

        entropy = belief_state.get_entropy()
        max_entropy = np.log2(6)
        min_entropy = 0

        # Should be between min and max
        assert min_entropy < entropy < max_entropy

    def test_get_evidence_count(self):
        """Test getting evidence count."""
        belief_state = BayesianBeliefState(dice_sides=6)

        assert belief_state.get_evidence_count() == 0

        # Add some evidence
        updates = [
            BeliefUpdate(comparison_results=["higher"]),
            BeliefUpdate(comparison_results=["lower"]),
        ]

        for i, update in enumerate(updates, 1):
            belief_state.update_beliefs(update)
            assert belief_state.get_evidence_count() == i

    def test_beliefs_sum_to_one(self):
        """Test that beliefs always sum to 1 after updates."""
        belief_state = BayesianBeliefState(dice_sides=6)

        updates = [
            BeliefUpdate(comparison_results=["higher"]),
            BeliefUpdate(comparison_results=["lower"]),
            BeliefUpdate(comparison_results=["same"]),
            BeliefUpdate(comparison_results=["higher"]),
        ]

        # Check initial sum
        assert abs(np.sum(belief_state.beliefs) - 1.0) < 1e-10

        # Check sum after each update
        for update in updates:
            belief_state.update_beliefs(update)
            assert abs(np.sum(belief_state.beliefs) - 1.0) < 1e-10

    def test_impossible_evidence_handling(self):
        """Test handling of evidence combinations that create zero likelihoods."""
        belief_state = BayesianBeliefState(dice_sides=6)

        # Apply a few "higher" results to favor lower targets
        for _ in range(3):
            update1 = BeliefUpdate(comparison_results=["higher"])
            belief_state.update_beliefs(update1)

        # Target 1 should be favored, target 6 should have zero probability
        prob_1 = belief_state.get_belief_for_target(1)
        prob_6 = belief_state.get_belief_for_target(6)

        assert prob_1 > 0  # Target 1 should have some probability
        assert abs(prob_6 - 0.0) < 1e-10  # Target 6 should have zero probability

        # Apply more evidence and verify probabilities still sum to 1
        update2 = BeliefUpdate(comparison_results=["lower"])
        belief_state.update_beliefs(update2)

        total_prob = sum(belief_state.get_belief_for_target(i) for i in range(1, 7))
        assert abs(total_prob - 1.0) < 1e-10  # Should still sum to 1
