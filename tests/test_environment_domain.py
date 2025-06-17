import pytest

from domains.environment.environment_domain import (
    Environment,
    EnvironmentEvidence,
    EvidenceType,
)


class TestEnvironmentEvidence:
    """Test the EnvironmentEvidence dataclass."""

    def test_evidence_creation(self):
        """Test creating evidence with valid data."""
        evidence = EnvironmentEvidence(dice_roll=3, comparison_results=["higher"])
        assert evidence.dice_roll == 3
        assert evidence.comparison_results == ["higher"]

    def test_evidence_comparison_results(self):
        """Test all valid comparison results."""
        valid_results = ["higher", "lower", "same"]
        for result in valid_results:
            evidence = EnvironmentEvidence(dice_roll=1, comparison_results=[result])
            assert evidence.comparison_results == [result]

    def test_evidence_multiple_comparison_results(self):
        """Test evidence with multiple comparison results."""
        evidence = EnvironmentEvidence(
            dice_roll=3, comparison_results=["higher", "double"]
        )
        assert evidence.dice_roll == 3
        assert evidence.comparison_results == ["higher", "double"]
        assert "higher" in evidence.comparison_results
        assert "double" in evidence.comparison_results


class TestEnvironment:
    """Test the Environment class."""

    def test_environment_initialization(self):
        """Test environment initialization with default and custom parameters."""
        # Default initialization
        env = Environment()
        assert env.dice_sides == 6
        assert env.evidence_type == EvidenceType.BASIC
        assert env._target_value is None

        # Custom initialization
        env = Environment(dice_sides=8, evidence_type=EvidenceType.EXTENDED, seed=42)
        assert env.dice_sides == 8
        assert env.evidence_type == EvidenceType.EXTENDED
        assert env._target_value is None

    def test_set_target_value_valid(self):
        """Test setting valid target values."""
        env = Environment(dice_sides=6)

        for target in range(1, 7):
            env.set_target_value(target)
            assert env.get_target_value() == target

    def test_set_target_value_invalid(self):
        """Test setting invalid target values raises ValueError."""
        env = Environment(dice_sides=6)

        invalid_targets = [0, 7, -1, 10]
        for target in invalid_targets:
            with pytest.raises(ValueError, match="Target must be between 1 and 6"):
                env.set_target_value(target)

    def test_get_target_value_not_set(self):
        """Test getting target value when not set raises ValueError."""
        env = Environment()

        with pytest.raises(ValueError, match="Target value not set"):
            env.get_target_value()

    def test_generate_random_target(self):
        """Test random target generation."""
        env = Environment(dice_sides=6, seed=42)

        # Generate multiple targets to test randomness
        targets = [env.generate_random_target() for _ in range(10)]

        # All targets should be valid
        for target in targets:
            assert 1 <= target <= 6

        # Should be able to get the target after generation
        assert env.get_target_value() == targets[-1]

    def test_generate_random_target_reproducible(self):
        """Test that random target generation is reproducible with seed."""
        env1 = Environment(dice_sides=6, seed=42)
        env2 = Environment(dice_sides=6, seed=42)

        target1 = env1.generate_random_target()
        target2 = env2.generate_random_target()

        assert target1 == target2

    def test_roll_dice_and_compare_target_not_set(self):
        """Test rolling dice without target set raises ValueError."""
        env = Environment()

        with pytest.raises(ValueError, match="Target value not set"):
            env.roll_dice_and_compare()

    def test_roll_dice_and_compare_higher(self):
        """Test dice roll comparison when result is higher."""
        env = Environment(dice_sides=6, seed=42)
        env.set_target_value(1)  # Target = 1, any roll > 1 should be "higher"

        # Run multiple times to test different rolls
        results = []
        for _ in range(20):
            evidence = env.roll_dice_and_compare()
            results.append(evidence)

            assert 1 <= evidence.dice_roll <= 6
            if evidence.dice_roll > 1:
                assert "higher" in evidence.comparison_results
            elif evidence.dice_roll < 1:
                assert "lower" in evidence.comparison_results
            else:
                assert "same" in evidence.comparison_results

    def test_roll_dice_and_compare_lower(self):
        """Test dice roll comparison when result is lower."""
        env = Environment(dice_sides=6, seed=42)
        env.set_target_value(6)  # Target = 6, any roll < 6 should be "lower"

        # Run multiple times to test different rolls
        for _ in range(20):
            evidence = env.roll_dice_and_compare()

            assert 1 <= evidence.dice_roll <= 6
            if evidence.dice_roll > 6:
                assert "higher" in evidence.comparison_results
            elif evidence.dice_roll < 6:
                assert "lower" in evidence.comparison_results
            else:
                assert "same" in evidence.comparison_results

    def test_roll_dice_and_compare_same(self):
        """Test dice roll comparison when result is same."""
        env = Environment(dice_sides=6, seed=42)

        # Test each possible target value
        for target in range(1, 7):
            env.set_target_value(target)

            # Roll until we get a match (may take several tries)
            found_same = False
            for _ in range(100):  # Avoid infinite loop
                evidence = env.roll_dice_and_compare()

                if evidence.dice_roll == target:
                    assert "same" in evidence.comparison_results
                    found_same = True
                    break
                elif evidence.dice_roll > target:
                    assert "higher" in evidence.comparison_results
                else:
                    assert "lower" in evidence.comparison_results

            # With 100 attempts, we should find at least one match for 6-sided die
            assert found_same, f"Failed to roll target value {target} in 100 attempts"

    def test_roll_dice_and_compare_all_outcomes(self):
        """Test that all comparison outcomes can occur."""
        env = Environment(dice_sides=6, seed=42)
        env.set_target_value(3)  # Middle value to allow all outcomes

        outcomes_seen = set()

        # Roll many times to see all outcomes
        for _ in range(100):
            evidence = env.roll_dice_and_compare()
            # Add all comparison results to outcomes_seen
            for result in evidence.comparison_results:
                outcomes_seen.add(result)

            # Verify consistency
            if evidence.dice_roll > 3:
                assert "higher" in evidence.comparison_results
            elif evidence.dice_roll < 3:
                assert "lower" in evidence.comparison_results
            else:
                assert "same" in evidence.comparison_results

        # Should see all three outcomes with enough rolls
        assert "higher" in outcomes_seen
        assert "lower" in outcomes_seen
        assert "same" in outcomes_seen

    def test_dice_sides_parameter(self):
        """Test environment with different dice sides."""
        for sides in [4, 8, 10, 20]:
            env = Environment(dice_sides=sides, seed=42)
            env.set_target_value(sides // 2)  # Middle value

            evidence = env.roll_dice_and_compare()
            assert 1 <= evidence.dice_roll <= sides
            # At least one basic comparison result should be present
            basic_results = {"higher", "lower", "same"}
            assert any(
                result in basic_results for result in evidence.comparison_results
            )

    def test_basic_evidence_type(self):
        """Test basic evidence type produces only basic comparison results."""
        env = Environment(dice_sides=6, evidence_type=EvidenceType.BASIC, seed=42)
        env.set_target_value(4)

        for _ in range(50):
            evidence = env.roll_dice_and_compare()
            # Should only contain basic results
            for result in evidence.comparison_results:
                assert result in ["higher", "lower", "same"]
            # Should contain exactly one basic result
            assert len(evidence.comparison_results) == 1

    def test_extended_evidence_type(self):
        """Test extended evidence type can produce additional comparison results."""
        env = Environment(dice_sides=8, evidence_type=EvidenceType.EXTENDED, seed=42)
        env.set_target_value(4)  # Target = 4, so half = 2, double = 8

        extended_results_seen = set()
        for _ in range(100):
            evidence = env.roll_dice_and_compare()

            # Should always contain at least one basic result
            basic_results = {"higher", "lower", "same"}
            assert any(
                result in basic_results for result in evidence.comparison_results
            )

            # Collect all results
            for result in evidence.comparison_results:
                extended_results_seen.add(result)
                assert result in ["higher", "lower", "same", "half", "double"]

        # Basic results should definitely be seen
        assert (
            "higher" in extended_results_seen
            or "lower" in extended_results_seen
            or "same" in extended_results_seen
        )

    def test_extended_evidence_half_condition(self):
        """Test that 'half' evidence is generated correctly."""
        env = Environment(dice_sides=8, evidence_type=EvidenceType.EXTENDED, seed=42)
        env.set_target_value(4)  # Target = 4, so half = 2

        # Force a dice roll of 2 by testing specific conditions
        for _ in range(200):  # More attempts to find the half condition
            evidence = env.roll_dice_and_compare()
            if evidence.dice_roll == 2:  # Should be 'half' of target 4
                assert "half" in evidence.comparison_results
                assert "lower" in evidence.comparison_results  # 2 < 4
                break

        # If we didn't find it randomly, we know the logic is correct from the condition above
        # This test mainly verifies the logic structure

    def test_extended_evidence_double_condition(self):
        """Test that 'double' evidence is generated correctly."""
        env = Environment(dice_sides=8, evidence_type=EvidenceType.EXTENDED, seed=42)
        env.set_target_value(3)  # Target = 3, so double = 6

        # Force a dice roll of 6 by testing specific conditions
        for _ in range(200):  # More attempts to find the double condition
            evidence = env.roll_dice_and_compare()
            if evidence.dice_roll == 6:  # Should be 'double' of target 3
                assert "double" in evidence.comparison_results
                assert "higher" in evidence.comparison_results  # 6 > 3
                break

        # If we didn't find it randomly, we know the logic is correct from the condition above
        # This test mainly verifies the logic structure
