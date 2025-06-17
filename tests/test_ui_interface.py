"""
Tests for the Gradio UI interface to ensure proper error handling and memory management.
"""

import matplotlib.pyplot as plt

from ui.gradio_interface import GradioInterface


class TestGradioInterface:
    """Test the Gradio interface functionality."""

    def test_interface_initialization(self):
        """Test that interface initializes correctly."""
        interface = GradioInterface()
        assert interface.game is not None
        assert interface.game.dice_sides == 6
        assert interface.game.max_rounds == 10

    def test_reset_game_returns_proper_types(self):
        """Test that reset_game returns proper types."""
        interface = GradioInterface()
        result = interface.reset_game(dice_sides=8, max_rounds=15)

        assert len(result) == 3
        status, belief_chart, game_log = result

        assert isinstance(status, str)
        assert isinstance(belief_chart, plt.Figure)
        assert isinstance(game_log, str)

    def test_start_new_game_valid_target(self):
        """Test starting a new game with valid target."""
        interface = GradioInterface()
        result = interface.start_new_game("3")

        assert len(result) == 3
        status, belief_chart, game_log = result

        assert isinstance(status, str)
        assert isinstance(belief_chart, plt.Figure)
        assert isinstance(game_log, str)
        assert "Playing" in status

    def test_start_new_game_invalid_target(self):
        """Test starting a new game with invalid target returns proper types."""
        interface = GradioInterface()
        result = interface.start_new_game("10")  # Invalid for 6-sided die

        assert len(result) == 3
        status, belief_chart, game_log = result

        assert isinstance(status, str)
        assert isinstance(belief_chart, plt.Figure)
        assert isinstance(game_log, str)
        assert "❌" in status
        assert "between 1 and 6" in status

    def test_play_round_without_game_started(self):
        """Test playing round without starting game returns proper types."""
        interface = GradioInterface()
        result = interface.play_round()

        assert len(result) == 3
        status, belief_chart, game_log = result

        assert isinstance(status, str)
        assert isinstance(belief_chart, plt.Figure)
        assert isinstance(game_log, str)
        assert "❌" in status
        assert "not in playing phase" in status

    def test_play_round_normal_flow(self):
        """Test normal round playing flow."""
        interface = GradioInterface()

        # Start a game first
        interface.start_new_game("3")

        # Play a round
        result = interface.play_round()

        assert len(result) == 3
        status, belief_chart, game_log = result

        assert isinstance(status, str)
        assert isinstance(belief_chart, plt.Figure)
        assert isinstance(game_log, str)
        assert "Playing" in status

    def test_exceeding_max_rounds(self):
        """Test that exceeding max rounds shows graceful completion."""
        interface = GradioInterface()

        # Start a game with 2 rounds
        interface.reset_game(dice_sides=6, max_rounds=2)
        interface.start_new_game("3")

        # Play 2 rounds (should finish the game)
        interface.play_round()
        interface.play_round()

        # Try to play another round (should be prevented)
        result = interface.play_round()

        assert len(result) == 3
        status, belief_chart, game_log = result

        assert isinstance(status, str)
        assert isinstance(belief_chart, plt.Figure)
        assert isinstance(game_log, str)
        # When game is finished, we should get a graceful completion message
        assert "🏁" in status and "completed" in status

    def test_create_empty_chart(self):
        """Test that empty chart creation works properly."""
        interface = GradioInterface()
        chart = interface._create_empty_chart()

        assert isinstance(chart, plt.Figure)
        # Clean up
        plt.close(chart)

    def test_matplotlib_memory_management(self):
        """Test that matplotlib figures are properly managed."""
        interface = GradioInterface()

        # Get initial figure count
        initial_figures = len(plt.get_fignums())

        # Create multiple charts
        for _ in range(5):
            interface._create_belief_chart()

        # Should not accumulate figures due to plt.close('all')
        final_figures = len(plt.get_fignums())

        # Should have at most 1 figure open (the most recent one)
        assert final_figures <= initial_figures + 1

    def test_error_handling_preserves_types(self):
        """Test that error handling always returns consistent types."""
        interface = GradioInterface()

        # Test various error conditions
        error_results = [
            interface.start_new_game("invalid_number"),
            interface.start_new_game("0"),
            interface.start_new_game("100"),
            interface.play_round(),  # No game started
        ]

        for result in error_results:
            assert len(result) == 3
            status, belief_chart, game_log = result

            assert isinstance(status, str)
            assert isinstance(belief_chart, plt.Figure)
            assert isinstance(game_log, str)
            assert "❌" in status

            # Clean up the figure
            plt.close(belief_chart)

    def test_game_log_creation(self):
        """Test that game log is created properly."""
        interface = GradioInterface()
        interface.start_new_game("3")

        # Play a few rounds
        for _ in range(3):
            interface.play_round()

        result = interface._get_interface_state()
        status, belief_chart, game_log = result

        assert isinstance(game_log, str)
        assert "Evidence History" in game_log
        assert "Round" in game_log

        # Clean up
        plt.close(belief_chart)

    def test_graceful_game_completion(self):
        """Test that game completion shows comprehensive final results."""
        interface = GradioInterface()

        # Start and complete a game
        interface.reset_game(dice_sides=6, max_rounds=3)
        interface.start_new_game("4")

        # Play all rounds
        for _ in range(3):
            interface.play_round()

        # Get final state
        result = interface._get_interface_state()
        status, belief_chart, game_log = result

        # Should show comprehensive final results in game log
        # (round_info was removed for cleaner UI)
        assert "Game Completed" in game_log
        assert "Congratulations" in game_log or "Learning opportunity" in game_log
        assert "confidence in true target" in game_log

        # Chart should have final state title
        assert isinstance(belief_chart, plt.Figure)

        # Clean up
        plt.close(belief_chart)

    def test_completion_state_preservation(self):
        """Test that completion state preserves all information."""
        interface = GradioInterface()

        # Complete a game
        interface.reset_game(dice_sides=6, max_rounds=2)
        interface.start_new_game("3")
        interface.play_round()
        interface.play_round()

        # Try to play after completion - should preserve final state
        result = interface.play_round()
        status, belief_chart, game_log = result

        # Should still have all the final game information
        assert "🏁" in status
        assert "completed" in status
        # round_info was removed for cleaner UI
        assert len(game_log) > 50  # Should have complete evidence history
        assert isinstance(belief_chart, plt.Figure)

        # Clean up
        plt.close(belief_chart)
