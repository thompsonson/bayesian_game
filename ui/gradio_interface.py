import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any, Union

from domains.coordination.game_coordination import BayesianGame, GamePhase


class GradioInterface:
    """Gradio interface for the Bayesian Game."""

    def __init__(self):
        """Initialize the Gradio interface."""
        self.game = None
        self.reset_game()

    def reset_game(
        self, dice_sides: int = 6, max_rounds: int = 10
    ) -> Tuple[str, str, plt.Figure, str]:
        """Reset the game with new parameters.

        Args:
            dice_sides: Number of sides on the dice
            max_rounds: Maximum number of rounds

        Returns:
            Tuple of (status, round_info, belief_chart, game_log)
        """
        self.game = BayesianGame(dice_sides=dice_sides, max_rounds=max_rounds)
        return self._get_interface_state()

    def start_new_game(
        self, target_value: str = ""
    ) -> Tuple[str, str, plt.Figure, str]:
        """Start a new game.

        Args:
            target_value: Optional specific target value

        Returns:
            Tuple of (status, round_info, belief_chart, game_log)
        """
        try:
            target = int(target_value) if target_value.strip() else None
            if target is not None and not (1 <= target <= self.game.dice_sides):
                return (
                    f"❌ Target value must be between 1 and {self.game.dice_sides}",
                    "",
                    self._create_empty_chart(),
                    "",
                )

            self.game.start_new_game(target_value=target)
            return self._get_interface_state()
        except ValueError as e:
            return f"❌ Error: {str(e)}", "", self._create_empty_chart(), ""

    def play_round(self) -> Tuple[str, str, plt.Figure, str]:
        """Play one round of the game.

        Returns:
            Tuple of (status, round_info, belief_chart, game_log)
        """
        try:
            # Check if game is already finished - but still show the final state
            if self.game.is_game_finished():
                # Get the current final state but with a message about being finished
                status, round_info, belief_chart, game_log = self._get_interface_state()
                return (
                    "🏁 Game completed! All rounds finished. Start a new game to play again.",
                    round_info,
                    belief_chart,
                    game_log,
                )

            if self.game.game_state.phase != GamePhase.PLAYING:
                return (
                    "❌ Game not in playing phase. Start a new game first.",
                    "",
                    self._create_empty_chart(),
                    "",
                )

            self.game.play_round()
            return self._get_interface_state()
        except ValueError as e:
            return f"❌ Error: {str(e)}", "", self._create_empty_chart(), ""

    def _get_interface_state(self) -> Tuple[str, str, plt.Figure, str]:
        """Get current interface state.

        Returns:
            Tuple of (status, round_info, belief_chart, game_log)
        """
        state = self.game.get_current_state()

        # Status message
        if state.phase == GamePhase.SETUP:
            status = "🎯 Ready to start new game"
        elif state.phase == GamePhase.PLAYING:
            status = f"🎲 Playing - Round {state.round_number}/{state.max_rounds}"
        else:  # FINISHED
            correct = "✅" if self.game.was_final_guess_correct() else "❌"
            accuracy = self.game.get_final_guess_accuracy()
            status = f"{correct} Game finished! Final guess: {state.most_likely_target} (True: {state.target_value}) - Accuracy: {accuracy:.2f}"

        # Belief visualization
        belief_chart = self._create_belief_chart()

        # Game log
        game_log = self._create_game_log()

        round_info = ""

        return status, round_info, belief_chart, game_log

    def _create_belief_chart(self) -> plt.Figure:
        """Create belief distribution chart.

        Returns:
            Matplotlib figure showing belief distribution
        """
        # Close any existing figures to prevent memory leaks
        plt.close("all")

        fig, ax = plt.subplots(figsize=(10, 6))

        if self.game.game_state.current_beliefs:
            targets = list(range(1, len(self.game.game_state.current_beliefs) + 1))
            beliefs = self.game.game_state.current_beliefs

            bars = ax.bar(
                targets, beliefs, alpha=0.7, color="skyblue", edgecolor="navy"
            )

            # Highlight the most likely target
            if self.game.game_state.most_likely_target:
                most_likely_idx = self.game.game_state.most_likely_target - 1
                bars[most_likely_idx].set_color("orange")
                bars[most_likely_idx].set_alpha(1.0)

            # Highlight true target if known
            if self.game.game_state.target_value:
                true_target_idx = self.game.game_state.target_value - 1
                bars[true_target_idx].set_edgecolor("red")
                bars[true_target_idx].set_linewidth(3)

            ax.set_xlabel("Target Value")
            ax.set_ylabel("Belief Probability")

            # Enhanced title based on game state
            if self.game.game_state.phase == GamePhase.FINISHED:
                correct_indicator = (
                    "✅" if self.game.was_final_guess_correct() else "❌"
                )
                ax.set_title(f"Final Belief Distribution {correct_indicator}")
            else:
                ax.set_title("Player 2's Belief Distribution")

            ax.set_xticks(targets)
            ax.set_ylim(0, 1)
            ax.grid(True, alpha=0.3)

            # Add legend
            legend_elements = []
            if self.game.game_state.most_likely_target:
                legend_elements.append(
                    plt.Rectangle(
                        (0, 0), 1, 1, fc="orange", alpha=1.0, label="Most Likely"
                    )
                )
            if self.game.game_state.target_value:
                legend_elements.append(
                    plt.Rectangle(
                        (0, 0), 1, 1, fc="skyblue", ec="red", lw=3, label="True Target"
                    )
                )
            if legend_elements:
                ax.legend(handles=legend_elements)
        else:
            ax.text(
                0.5,
                0.5,
                "Start a game to see beliefs",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=14,
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        plt.tight_layout()
        return fig

    def _create_empty_chart(self) -> plt.Figure:
        """Create an empty chart for error states.

        Returns:
            Matplotlib figure with error message
        """
        # Close any existing figures to prevent memory leaks
        plt.close("all")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(
            0.5,
            0.5,
            "Error: Unable to display chart",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=14,
            color="red",
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title("Chart Error")
        plt.tight_layout()
        return fig

    def _create_game_log(self) -> str:
        """Create game log showing evidence history.

        Returns:
            Formatted string with game log
        """
        if not self.game.game_state.evidence_history:
            return "No evidence yet. Start playing rounds to see the log."

        log_lines = ["**Evidence History:**\n"]

        for i, evidence in enumerate(self.game.game_state.evidence_history, 1):
            emoji = {"higher": "⬆️", "lower": "⬇️", "same": "🎯"}[
                evidence.comparison_result
            ]
            log_lines.append(
                f"Round {i}: Rolled {evidence.dice_roll} → {evidence.comparison_result} {emoji}"
            )

        # Add completion message if game is finished
        if self.game.game_state.phase == GamePhase.FINISHED:
            log_lines.append("")
            log_lines.append("**🏁 Game Completed!**")

            if self.game.was_final_guess_correct():
                log_lines.append(
                    "🎉 **Congratulations!** Player 2 correctly identified the target!"
                )
            else:
                log_lines.append(
                    "📈 **Learning opportunity!** Player 2's beliefs converged but missed the target."
                )

            # Add some Bayesian insights
            final_accuracy = self.game.get_final_guess_accuracy()
            if final_accuracy > 0.5:
                log_lines.append(
                    f"🎯 Strong evidence: {final_accuracy:.1%} confidence in true target"
                )
            elif final_accuracy > 0.3:
                log_lines.append(
                    f"🤔 Moderate evidence: {final_accuracy:.1%} confidence in true target"
                )
            else:
                log_lines.append(
                    f"🌫️ Conflicting evidence: Only {final_accuracy:.1%} confidence in true target"
                )

        return "\n".join(log_lines)


def create_interface() -> gr.Interface:
    """Create and return the Gradio interface.

    Returns:
        Configured Gradio interface
    """
    interface = GradioInterface()

    with gr.Blocks(title="Bayesian Game", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎲 Bayesian Game")
        gr.Markdown(
            """
        **Game Rules:**
        - Judge and Player 1 can see the target die value
        - Player 2 must deduce the target value using Bayesian inference
        - Each round: Player 1 rolls dice and reports "higher"/"lower"/"same" compared to target
        - Game runs for a specified number of rounds
        """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Game Controls")

                with gr.Row():
                    dice_sides = gr.Number(
                        value=6, label="Dice Sides", minimum=2, maximum=20, precision=0
                    )
                    max_rounds = gr.Number(
                        value=10, label="Max Rounds", minimum=1, maximum=50, precision=0
                    )

                reset_btn = gr.Button("🔄 Reset Game", variant="secondary")

                target_input = gr.Textbox(
                    label="Target Value (optional)",
                    placeholder="Leave empty for random target",
                    max_lines=1,
                )
                start_btn = gr.Button("🎯 Start New Game", variant="primary")
                play_btn = gr.Button("🎲 Play Round", variant="secondary")

            with gr.Column(scale=2):
                status_output = gr.Textbox(label="Game Status", interactive=False)
                round_info = gr.Markdown("Start a new game to begin.")
                belief_plot = gr.Plot(label="Belief Distribution")
                game_log = gr.Markdown("Game log will appear here.")

        # Event handlers
        reset_btn.click(
            interface.reset_game,
            inputs=[dice_sides, max_rounds],
            outputs=[status_output, round_info, belief_plot, game_log],
        )

        start_btn.click(
            interface.start_new_game,
            inputs=[target_input],
            outputs=[status_output, round_info, belief_plot, game_log],
        )

        play_btn.click(
            interface.play_round,
            outputs=[status_output, round_info, belief_plot, game_log],
        )

        # Initialize interface
        demo.load(
            interface._get_interface_state,
            outputs=[status_output, round_info, belief_plot, game_log],
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
