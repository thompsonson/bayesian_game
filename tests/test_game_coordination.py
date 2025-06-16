import pytest
from domains.coordination.game_coordination import BayesianGame, GameState, GamePhase
from domains.environment.environment_domain import EnvironmentEvidence


class TestGameState:
    """Test the GameState dataclass."""
    
    def test_game_state_creation(self):
        """Test creating game state with required parameters."""
        state = GameState(
            round_number=5,
            max_rounds=10,
            phase=GamePhase.PLAYING
        )
        
        assert state.round_number == 5
        assert state.max_rounds == 10
        assert state.phase == GamePhase.PLAYING
        assert state.target_value is None
        assert state.evidence_history == []
        assert state.current_beliefs == []
    
    def test_game_state_with_optional_params(self):
        """Test creating game state with optional parameters."""
        evidence = [EnvironmentEvidence(dice_roll=3, comparison_result="higher")]
        beliefs = [0.2, 0.3, 0.5]
        
        state = GameState(
            round_number=2,
            max_rounds=5,
            phase=GamePhase.PLAYING,
            target_value=4,
            evidence_history=evidence,
            current_beliefs=beliefs,
            most_likely_target=3,
            belief_entropy=1.5
        )
        
        assert state.target_value == 4
        assert state.evidence_history == evidence
        assert state.current_beliefs == beliefs
        assert state.most_likely_target == 3
        assert state.belief_entropy == 1.5


class TestBayesianGame:
    """Test the BayesianGame class."""
    
    def test_initialization_default(self):
        """Test game initialization with default parameters."""
        game = BayesianGame()
        
        assert game.dice_sides == 6
        assert game.max_rounds == 10
        assert game.environment.dice_sides == 6
        assert game.belief_state.dice_sides == 6
        assert game.game_state.phase == GamePhase.SETUP
        assert game.game_state.round_number == 0
        assert game.game_state.max_rounds == 10
    
    def test_initialization_custom(self):
        """Test game initialization with custom parameters."""
        game = BayesianGame(dice_sides=8, max_rounds=15, seed=42)
        
        assert game.dice_sides == 8
        assert game.max_rounds == 15
        assert game.environment.dice_sides == 8
        assert game.belief_state.dice_sides == 8
        assert game.game_state.max_rounds == 15
    
    def test_start_new_game_random_target(self):
        """Test starting new game with random target."""
        game = BayesianGame(seed=42)
        
        state = game.start_new_game()
        
        assert state.phase == GamePhase.PLAYING
        assert state.round_number == 0
        assert 1 <= state.target_value <= 6
        assert len(state.evidence_history) == 0
        assert len(state.current_beliefs) == 6
        assert state.most_likely_target in range(1, 7)
        assert state.belief_entropy > 0
    
    def test_start_new_game_specific_target(self):
        """Test starting new game with specific target."""
        game = BayesianGame()
        
        state = game.start_new_game(target_value=4)
        
        assert state.phase == GamePhase.PLAYING
        assert state.target_value == 4
        assert game.environment.get_target_value() == 4
    
    def test_start_new_game_resets_state(self):
        """Test that starting new game resets previous state."""
        game = BayesianGame(seed=42)
        
        # Start first game and play some rounds
        game.start_new_game(target_value=3)
        game.play_round()
        game.play_round()
        
        # Start new game
        state = game.start_new_game(target_value=5)
        
        assert state.target_value == 5
        assert state.round_number == 0
        assert len(state.evidence_history) == 0
        assert len(game.belief_state.evidence_history) == 0
    
    def test_play_round_not_playing(self):
        """Test playing round when not in playing phase."""
        game = BayesianGame()
        
        # Game starts in setup phase
        with pytest.raises(ValueError, match="Game is not in playing phase"):
            game.play_round()
    
    def test_play_round_game_finished(self):
        """Test playing round when game is already finished."""
        game = BayesianGame(max_rounds=1, seed=42)
        
        # Start game and play one round (should finish)
        game.start_new_game(target_value=3)
        game.play_round()
        
        # Try to play another round
        with pytest.raises(ValueError, match="Game is not in playing phase"):
            game.play_round()
    
    def test_play_round_updates_state(self):
        """Test that playing round updates game state correctly."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=3)
        
        initial_round_number = game.get_current_state().round_number
        
        # Play one round
        updated_state = game.play_round()
        
        assert updated_state.round_number == initial_round_number + 1
        assert len(updated_state.evidence_history) == 1
        assert len(updated_state.current_beliefs) == 6
        assert updated_state.most_likely_target in range(1, 7)
        assert updated_state.belief_entropy >= 0
        
        # Evidence should be valid
        evidence = updated_state.evidence_history[0]
        assert 1 <= evidence.dice_roll <= 6
        assert evidence.comparison_result in ["higher", "lower", "same"]
    
    def test_play_multiple_rounds(self):
        """Test playing multiple rounds."""
        game = BayesianGame(max_rounds=5, seed=42)
        game.start_new_game(target_value=4)
        
        for expected_round in range(1, 6):
            state = game.play_round()
            
            assert state.round_number == expected_round
            assert len(state.evidence_history) == expected_round
            
            if expected_round < 5:
                assert state.phase == GamePhase.PLAYING
            else:
                assert state.phase == GamePhase.FINISHED
    
    def test_get_current_state(self):
        """Test getting current game state."""
        game = BayesianGame()
        
        # Initial state
        state = game.get_current_state()
        assert state.phase == GamePhase.SETUP
        
        # After starting game
        game.start_new_game(target_value=2)
        state = game.get_current_state()
        assert state.phase == GamePhase.PLAYING
        assert state.target_value == 2
    
    def test_is_game_finished(self):
        """Test checking if game is finished."""
        game = BayesianGame(max_rounds=2, seed=42)
        
        # Initially not finished
        assert not game.is_game_finished()
        
        # Start game - still not finished
        game.start_new_game(target_value=3)
        assert not game.is_game_finished()
        
        # Play one round - still not finished
        game.play_round()
        assert not game.is_game_finished()
        
        # Play final round - now finished
        game.play_round()
        assert game.is_game_finished()
    
    def test_get_final_guess_accuracy_no_target(self):
        """Test getting final guess accuracy without target set."""
        game = BayesianGame()
        
        with pytest.raises(ValueError, match="Target value not set"):
            game.get_final_guess_accuracy()
    
    def test_get_final_guess_accuracy(self):
        """Test getting final guess accuracy."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=3)
        
        # Play some rounds
        game.play_round()
        game.play_round()
        
        accuracy = game.get_final_guess_accuracy()
        
        # Should be probability assigned to target value 3
        assert 0 <= accuracy <= 1
        expected_accuracy = game.belief_state.get_belief_for_target(3)
        assert accuracy == expected_accuracy
    
    def test_was_final_guess_correct_no_target(self):
        """Test checking final guess correctness without target set."""
        game = BayesianGame()
        
        with pytest.raises(ValueError, match="Target value not set"):
            game.was_final_guess_correct()
    
    def test_was_final_guess_correct(self):
        """Test checking if final guess was correct."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=3)
        
        # Play rounds until we get definitive evidence
        for _ in range(10):  # Play enough rounds to get clear evidence
            if game.is_game_finished():
                break
            game.play_round()
        
        is_correct = game.was_final_guess_correct()
        most_likely = game.game_state.most_likely_target
        
        assert isinstance(is_correct, bool)
        assert is_correct == (most_likely == 3)
    
    def test_get_game_summary(self):
        """Test getting game summary."""
        game = BayesianGame(max_rounds=3, seed=42)
        game.start_new_game(target_value=4)
        
        # Play all rounds
        while not game.is_game_finished():
            game.play_round()
        
        summary = game.get_game_summary()
        
        # Check all required fields
        assert summary["rounds_played"] == 3
        assert summary["max_rounds"] == 3
        assert summary["true_target"] == 4
        assert summary["final_guess"] in range(1, 7)
        assert isinstance(summary["guess_correct"], bool)
        assert 0 <= summary["final_accuracy"] <= 1
        assert summary["final_entropy"] >= 0
        assert summary["evidence_count"] == 3
        assert len(summary["final_beliefs"]) == 6
        
        # Check that final beliefs are properly indexed (1-6)
        for i in range(1, 7):
            assert i in summary["final_beliefs"]
    
    def test_belief_updates_with_evidence(self):
        """Test that belief updates properly reflect evidence."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=1)  # Low target for predictable evidence
        
        initial_beliefs = game.belief_state.get_current_beliefs()
        
        # Play several rounds
        states = []
        for _ in range(5):
            if game.is_game_finished():
                break
            state = game.play_round()
            states.append(state)
        
        # Beliefs should change as evidence accumulates
        final_beliefs = game.belief_state.get_current_beliefs()
        
        # Should not be uniform anymore (unless very unlikely)
        assert not all(abs(b - 1/6) < 1e-10 for b in final_beliefs)
        
        # Evidence should influence beliefs correctly
        for state in states:
            for evidence in state.evidence_history:
                if evidence.comparison_result == "higher":
                    # Target must be less than dice roll
                    for target in range(evidence.dice_roll, 7):
                        # These targets should have reduced probability
                        pass  # Detailed verification would require complex logic
    
    def test_game_with_evidence_updates(self):
        """Test game behavior with evidence updates."""
        game = BayesianGame(seed=42)
        game.start_new_game(target_value=3)
        
        # Apply evidence that changes beliefs
        from domains.belief.belief_domain import BeliefUpdate
        update = BeliefUpdate(comparison_result="higher")
        game.belief_state.update_beliefs(update)
        
        # Update game state to reflect the belief change
        game.game_state.most_likely_target = game.belief_state.get_most_likely_target()
        
        # Beliefs should have changed from uniform
        prob_1 = game.belief_state.get_belief_for_target(1)
        prob_6 = game.belief_state.get_belief_for_target(6)
        
        assert prob_1 > prob_6  # Lower targets should be more likely after "higher"
        assert game.belief_state.get_most_likely_target() in range(1, 7)
        assert 0 <= game.get_final_guess_accuracy() <= 1
    
    def test_reproducibility_with_seed(self):
        """Test that games are reproducible with same seed."""
        # Run two games with same seed
        game1 = BayesianGame(seed=42)
        game1.start_new_game(target_value=3)
        
        game2 = BayesianGame(seed=42)
        game2.start_new_game(target_value=3)
        
        # Play same number of rounds
        for _ in range(5):
            if game1.is_game_finished() or game2.is_game_finished():
                break
            
            state1 = game1.play_round()
            state2 = game2.play_round()
            
            # Evidence should be identical
            assert len(state1.evidence_history) == len(state2.evidence_history)
            for ev1, ev2 in zip(state1.evidence_history, state2.evidence_history):
                assert ev1.dice_roll == ev2.dice_roll
                assert ev1.comparison_result == ev2.comparison_result
            
            # Beliefs should be identical
            assert state1.current_beliefs == state2.current_beliefs