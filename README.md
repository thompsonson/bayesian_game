---
title: Bayesian Game
emoji: 🎲
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
license: mit
---

# 🎲 Bayesian Game

A Bayesian Game implementation featuring a Belief-based Agent using domain-driven design. This interactive game demonstrates Bayesian inference in action as Player 2 attempts to deduce a hidden target die value based on evidence from dice rolls.

## 🎯 Game Overview

**The Setup:**
- Judge and Player 1 can see the target die value (1-6)
- Player 2 must deduce the target value using Bayesian inference
- Each round: Player 1 rolls dice and reports "higher"/"lower"/"same" compared to target
- **Player 2 only receives the comparison result, NOT the actual dice roll value**
- Game runs for 10 rounds (configurable)
- Judge ensures truth-telling

**The Challenge:**
Player 2 starts with uniform beliefs about the target value and updates their beliefs after each piece of evidence using Bayes' rule. The key insight is that Player 2 must calculate the probability that ANY dice roll would produce the observed comparison result for each possible target value.

## 🏗️ Architecture

Built using **Domain-Driven Design** with clean separation of concerns:

### 1. Environment Domain (`domains/environment/`)
- **Pure evidence generation** - no probability knowledge
- `EnvironmentEvidence`: Dataclass for dice roll results
- `Environment`: Generates target values and dice roll comparisons

### 2. Belief Domain (`domains/belief/`)
- **Pure Bayesian inference** - receives only comparison results, no dice roll values
- `BeliefUpdate`: Dataclass containing only comparison results
- `BayesianBeliefState`: Calculates likelihood P(comparison_result | target) for each possible target

### 3. Game Coordination (`domains/coordination/`)
- **Thin orchestration layer** - coordinates between domains
- `GameState`: Tracks current game state
- `BayesianGame`: Main game orchestration class

### 4. UI Layer (`ui/`)
- Interactive Gradio web interface
- Real-time belief visualization
- Game controls and statistics display

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone and navigate to the project:**
```bash
git clone <repository-url>
cd bayesian_game
```

2. **Set up virtual environment:**
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using pip
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
# Using uv
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

4. **Set up pre-commit hooks (optional for development):**
```bash
pre-commit install
```

### Running the Game

**Launch the interactive web interface:**
```bash
python app.py
```

The game will be available at `http://localhost:7860`

**Run from command line (for development):**
```python
from domains.coordination.game_coordination import BayesianGame

# Create and start a game
game = BayesianGame(seed=42)
game.start_new_game(target_value=3)

# Play rounds
for round_num in range(5):
    state = game.play_round()
    evidence = state.evidence_history[-1]
    print(f"Round {round_num + 1}: Rolled {evidence.dice_roll} → {evidence.comparison_result}")
    print(f"Most likely target: {state.most_likely_target}")
    print(f"Belief entropy: {state.belief_entropy:.2f}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific domain tests
python -m pytest tests/test_environment_domain.py -v
python -m pytest tests/test_belief_domain.py -v
python -m pytest tests/test_game_coordination.py -v

# Run with coverage
python -m pytest tests/ --cov=domains --cov-report=html
```

**Test Coverage:**
- 56 comprehensive tests
- All core functionality covered
- Edge cases and error handling tested
- Reproducibility and randomness testing

## 🎮 Game Interface

The Gradio interface provides:

- **Game Controls**: Start new games, play rounds, reset settings
- **Real-time Visualization**: Belief probability distribution chart
- **Game Statistics**: Entropy, accuracy, round information
- **Evidence History**: Complete log of dice rolls and comparisons
- **Customization**: Adjustable dice sides and round count

### Interface Features

- 📊 **Belief Distribution Chart**: Visual representation of Player 2's beliefs
- 🎯 **Target Highlighting**: True target and most likely guess highlighted
- 📝 **Evidence Log**: Complete history of all dice rolls and results
- ⚙️ **Game Settings**: Customize dice sides (2-20) and max rounds (1-50)
- 🔄 **Reset & Replay**: Easy game reset and replay functionality

## 📁 Project Structure

```
bayesian_game/
├── domains/                    # Core domain logic
│   ├── environment/           # Evidence generation
│   │   └── environment_domain.py
│   ├── belief/               # Bayesian inference
│   │   └── belief_domain.py
│   └── coordination/         # Game orchestration
│       └── game_coordination.py
├── ui/                       # User interface
│   └── gradio_interface.py
├── tests/                    # Comprehensive test suite
│   ├── test_environment_domain.py
│   ├── test_belief_domain.py
│   └── test_game_coordination.py
├── app.py                    # Main entry point
├── requirements.txt          # Dependencies
├── CLAUDE.md                 # Project specifications
└── README.md                 # This file
```

## 🔬 Key Features

### Bayesian Inference Engine
- **Proper Bayesian Updates**: Uses Bayes' rule for belief updates
- **Entropy Calculation**: Measures uncertainty in beliefs
- **Evidence Integration**: Combines multiple pieces of evidence
- **Impossible Evidence Handling**: Gracefully handles contradictory evidence

### Reproducible Experiments
- **Seeded Randomness**: Reproducible results for testing
- **Deterministic Behavior**: Same seed produces same game sequence
- **Statistical Analysis**: Track accuracy and convergence

### Clean Architecture
- **Domain Separation**: Pure domains with no cross-dependencies
- **Testable Components**: Each domain independently testable
- **Extensible Design**: Easy to add new features or modify rules

## 🎓 Educational Value

This implementation demonstrates:

- **Bayesian Inference**: Real-world application of Bayes' rule
- **Uncertainty Quantification**: How beliefs evolve with evidence
- **Information Theory**: Entropy as a measure of uncertainty
- **Domain-Driven Design**: Clean software architecture patterns
- **Test-Driven Development**: Comprehensive testing strategies

## 🛠️ Development

### Key Dependencies
- `gradio`: Web interface framework
- `numpy`: Numerical computations for Bayesian inference
- `matplotlib`: Belief distribution visualization
- `pytest`: Testing framework
- `pre-commit`: Code quality automation
- `ruff`: Fast Python linter and formatter (replaces Black, isort, flake8)

### Development Workflow
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files

# Run tests with coverage
python -m pytest tests/ --cov=domains --cov=ui --cov-report=html

# Code formatting and linting (automatic with pre-commit)
ruff check --fix .
ruff format .
mypy .
```

### CI/CD Pipeline
- **GitHub Actions**: Automated testing on Python 3.10, 3.11, 3.12
- **Pre-commit hooks**: Code quality checks (Ruff, mypy, bandit)
- **Test coverage**: Comprehensive coverage reporting
- **Security scanning**: Trivy vulnerability scanner
- **Auto-deployment**: Pushes to Hugging Face Spaces on main branch

### Design Principles
1. **Pure Functions**: Domains contain pure, testable functions
2. **Immutable Data**: Evidence and belief updates are immutable
3. **Clear Interfaces**: Well-defined boundaries between domains
4. **Comprehensive Testing**: Every component thoroughly tested

### Contributing
1. Follow the existing domain-driven architecture
2. Add tests for any new functionality
3. Maintain clean separation between domains
4. Update documentation for new features

## 📊 Example Game Flow

```
Round 1: Evidence "higher" (dice roll > target)
├─ P(roll>1)=5/6, P(roll>2)=4/6, ..., P(roll>6)=0/6
├─ Lower targets become more likely
└─ Entropy: 2.15 bits

Round 2: Evidence "lower" (dice roll < target)
├─ P(roll<1)=0/6, P(roll<2)=1/6, ..., P(roll<6)=5/6
├─ Higher targets become more likely
└─ Entropy: 1.97 bits

Round 3: Evidence "same" (dice roll = target)
├─ P(roll=target) = 1/6 for all targets
├─ Beliefs remain proportional to previous round
└─ Entropy: 1.97 bits (unchanged)
```

## 🚀 Deployment

### Hugging Face Spaces (Automated)

The repository includes automated deployment to Hugging Face Spaces via GitHub Actions. To set this up:

1. **Create a Hugging Face Space**: Go to [hf.co/new-space](https://hf.co/new-space) and create a new Gradio space
2. **Get your HF Token**: Visit [hf.co/settings/tokens](https://hf.co/settings/tokens) and create a token with write access
3. **Add GitHub Secret**: In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:
   - Name: `HF_TOKEN`
   - Value: Your Hugging Face token
4. **Update workflow**: Edit `.github/workflows/deploy.yml` and replace:
   - `HF_USERNAME`: Your Hugging Face username
   - `HF_SPACE_NAME`: Your space name

The deployment will automatically trigger after successful CI runs on the main branch.

### Other Deployment Options

- **Local Server**: Built-in Gradio server (`python app.py`)
- **Cloud Platforms**: Standard Python web app deployment

---

**Built with ❤️ using Domain-Driven Design and Bayesian Inference**
