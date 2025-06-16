"""
Bayesian Game - Hugging Face entry point

A Bayesian Game implementation featuring a Belief-based Agent using domain-driven design.
"""

from ui.gradio_interface import create_interface


def main():
    """Main entry point for the Bayesian Game application."""
    demo = create_interface()
    
    # Launch with Hugging Face compatible settings
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public sharing if needed
        show_error=True
    )


if __name__ == "__main__":
    main()