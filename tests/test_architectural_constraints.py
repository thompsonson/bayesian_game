"""
Architectural constraint tests to ensure proper domain separation.

These tests verify that the key architectural principles are maintained:
1. Belief domain receives only comparison results, not dice roll values
2. Information flows correctly through the coordination layer
3. Domain boundaries are properly enforced
"""

import pytest
import inspect
from domains.belief.belief_domain import BeliefUpdate, BayesianBeliefState
from domains.environment.environment_domain import EnvironmentEvidence
from domains.coordination.game_coordination import BayesianGame


class TestArchitecturalConstraints:
    """Test architectural constraints and domain separation."""

    def test_belief_update_dataclass_structure(self):
        """Test that BeliefUpdate contains only comparison_result field."""
        # Get all fields of BeliefUpdate
        fields = BeliefUpdate.__dataclass_fields__
        
        # Should only contain comparison_result
        assert len(fields) == 1, f"BeliefUpdate should have exactly 1 field, got {len(fields)}: {list(fields.keys())}"
        assert "comparison_result" in fields, "BeliefUpdate must contain comparison_result field"
        assert "dice_roll" not in fields, "BeliefUpdate MUST NOT contain dice_roll field"

    def test_environment_evidence_dataclass_structure(self):
        """Test that EnvironmentEvidence contains both dice_roll and comparison_result."""
        # Get all fields of EnvironmentEvidence
        fields = EnvironmentEvidence.__dataclass_fields__
        
        # Should contain both fields
        assert len(fields) == 2, f"EnvironmentEvidence should have exactly 2 fields, got {len(fields)}: {list(fields.keys())}"
        assert "dice_roll" in fields, "EnvironmentEvidence must contain dice_roll field"
        assert "comparison_result" in fields, "EnvironmentEvidence must contain comparison_result field"

    def test_belief_state_methods_no_dice_roll_parameters(self):
        """Test that BayesianBeliefState methods don't accept dice_roll parameters."""
        # Get all methods of BayesianBeliefState
        methods = inspect.getmembers(BayesianBeliefState, predicate=inspect.isfunction)
        
        for method_name, method in methods:
            if method_name.startswith('_'):
                continue  # Skip private methods
                
            signature = inspect.signature(method)
            param_names = list(signature.parameters.keys())
            
            assert "dice_roll" not in param_names, f"Method {method_name} MUST NOT have dice_roll parameter"

    def test_belief_update_creation_without_dice_roll(self):
        """Test that BeliefUpdate can be created without dice_roll."""
        # This should work (only comparison_result)
        update = BeliefUpdate(comparison_result="higher")
        assert update.comparison_result == "higher"
        
        # This should fail if dice_roll field exists
        try:
            # This should raise TypeError if dice_roll is not a field
            BeliefUpdate(dice_roll=3, comparison_result="higher")
            pytest.fail("BeliefUpdate should not accept dice_roll parameter")
        except TypeError:
            pass  # Expected - dice_roll should not be a valid parameter

    def test_information_filtering_in_coordination(self):
        """Test that game coordination properly filters information to belief domain."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=3)
        
        # Get initial belief state
        initial_beliefs = game.belief_state.get_current_beliefs()
        
        # Play a round (this should trigger proper information filtering)
        game.play_round()
        
        # Verify that belief state received update (beliefs changed)
        updated_beliefs = game.belief_state.get_current_beliefs()
        assert not all(a == b for a, b in zip(initial_beliefs, updated_beliefs)), \
            "Beliefs should change after receiving evidence"
        
        # Verify that evidence history in belief domain contains only comparison results
        for evidence in game.belief_state.evidence_history:
            assert hasattr(evidence, "comparison_result"), "Belief evidence must have comparison_result"
            assert not hasattr(evidence, "dice_roll"), "Belief evidence MUST NOT have dice_roll"

    def test_domain_import_isolation(self):
        """Test that belief domain doesn't import environment domain."""
        import domains.belief.belief_domain as belief_module
        
        # Get all imports in the belief domain module
        belief_source = inspect.getsource(belief_module)
        
        # Should not import environment domain
        assert "from domains.environment" not in belief_source, \
            "Belief domain MUST NOT import environment domain"
        assert "import domains.environment" not in belief_source, \
            "Belief domain MUST NOT import environment domain"

    def test_proper_bayesian_calculation_structure(self):
        """Test that belief updates use probabilistic calculations."""
        belief_state = BayesianBeliefState(dice_sides=6)
        
        # Apply "higher" evidence
        update = BeliefUpdate(comparison_result="higher")
        belief_state.update_beliefs(update)
        
        # Verify that probabilities follow expected pattern for "higher"
        # Target 1: P(roll > 1) = 5/6, should be highest
        # Target 6: P(roll > 6) = 0/6, should be zero
        prob_1 = belief_state.get_belief_for_target(1)
        prob_6 = belief_state.get_belief_for_target(6)
        
        assert prob_1 > prob_6, "Higher evidence should favor lower targets"
        assert abs(prob_6 - 0.0) < 1e-10, "Target 6 should have zero probability after 'higher' evidence"

    def test_coordination_layer_responsibility(self):
        """Test that coordination layer properly orchestrates without leaking information."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=4)
        
        # Play a round to generate evidence
        state = game.play_round()
        
        # Game state should have full information (for display)
        assert hasattr(state.evidence_history[0], "dice_roll"), \
            "Game state should maintain full evidence for display"
        assert hasattr(state.evidence_history[0], "comparison_result"), \
            "Game state should maintain comparison results"
        
        # But belief state should only have comparison results
        belief_evidence = game.belief_state.evidence_history[0]
        assert hasattr(belief_evidence, "comparison_result"), \
            "Belief evidence must have comparison_result"
        assert not hasattr(belief_evidence, "dice_roll"), \
            "Belief evidence MUST NOT have dice_roll"

    def test_no_hard_coded_probabilities(self):
        """Test that belief calculations are dynamic, not hard-coded."""
        # Test with different dice sides to ensure calculations are dynamic
        for dice_sides in [4, 6, 8, 10]:
            belief_state = BayesianBeliefState(dice_sides=dice_sides)
            
            # Apply "higher" evidence
            update = BeliefUpdate(comparison_result="higher")
            belief_state.update_beliefs(update)
            
            # Target 1 should have highest probability: P(roll > 1) = (dice_sides - 1) / dice_sides
            # Last target should have zero probability: P(roll > dice_sides) = 0
            prob_1 = belief_state.get_belief_for_target(1)
            prob_last = belief_state.get_belief_for_target(dice_sides)
            
            expected_prob_1_unnormalized = (dice_sides - 1) / dice_sides
            
            assert prob_1 > prob_last, f"Target 1 should be more likely than target {dice_sides}"
            assert abs(prob_last - 0.0) < 1e-10, f"Target {dice_sides} should have zero probability"
            assert prob_1 > 0, "Target 1 should have non-zero probability"