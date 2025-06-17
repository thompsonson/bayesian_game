import pytest

from domains.environment.environment_domain import Environment, EnvironmentEvidence


class TestEnvironmentEvidence:
    """Test the EnvironmentEvidence dataclass."""

    def test_evidence_creation(self):
        """Test creating evidence with valid data."""
        evidence = EnvironmentEvidence(dice_roll=3, comparison_result="higher")
        assert evidence.dice_roll == 3
        assert evidence.comparison_result == "higher"

    def test_evidence_comparison_results(self):
        """Test all valid comparison results."""
        valid_results = ["higher", "lower", "same"]
        for result in valid_results:
            evidence = EnvironmentEvidence(dice_roll=1, comparison_result=result)
            assert evidence.comparison_result == result


class TestEnvironment:
    """Test the Environment class."""

    def test_environment_initialization(self):
        """Test environment initialization with default and custom parameters."""
        # Default initialization
        env = Environment()
        assert env.dice_sides == 6
        assert env._target_value is None

        # Custom initialization
        env = Environment(dice_sides=8, seed=42)
        assert env.dice_sides == 8
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
                assert evidence.comparison_result == "higher"
            elif evidence.dice_roll < 1:
                assert evidence.comparison_result == "lower"
            else:
                assert evidence.comparison_result == "same"

    def test_roll_dice_and_compare_lower(self):
        """Test dice roll comparison when result is lower."""
        env = Environment(dice_sides=6, seed=42)
        env.set_target_value(6)  # Target = 6, any roll < 6 should be "lower"

        # Run multiple times to test different rolls
        for _ in range(20):
            evidence = env.roll_dice_and_compare()

            assert 1 <= evidence.dice_roll <= 6
            if evidence.dice_roll > 6:
                assert evidence.comparison_result == "higher"
            elif evidence.dice_roll < 6:
                assert evidence.comparison_result == "lower"
            else:
                assert evidence.comparison_result == "same"

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
                    assert evidence.comparison_result == "same"
                    found_same = True
                    break
                elif evidence.dice_roll > target:
                    assert evidence.comparison_result == "higher"
                else:
                    assert evidence.comparison_result == "lower"

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
            outcomes_seen.add(evidence.comparison_result)

            # Verify consistency
            if evidence.dice_roll > 3:
                assert evidence.comparison_result == "higher"
            elif evidence.dice_roll < 3:
                assert evidence.comparison_result == "lower"
            else:
                assert evidence.comparison_result == "same"

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
            assert evidence.comparison_result in ["higher", "lower", "same"]
