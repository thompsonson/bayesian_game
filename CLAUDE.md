# Bayesian Game Project

## Project Overview
A Bayesian Game implementation featuring a Belief-based Agent using domain-driven design.

## Game Rules
- Judge and Player 1 can see the target die value
- Player 2 must deduce the target value using only comparison results
- Player 1 rolls dice and reports evidence based on selected evidence type
- **CRITICAL**: Player 2 receives ONLY the evidence results, NOT the dice roll value
- Game runs for 10 rounds
- Judge ensures truth-telling

### Evidence Types
**Basic Evidence**: `["higher", "lower", "same"]`
- Standard comparison between dice roll and target

**Extended Evidence**: `["higher", "lower", "same", "half", "double"]`
- Multiple evidence types can apply to single roll
- "half": dice_roll = target/2 (exact integer matches only)
- "double": dice_roll = target*2 (exact integer matches only)
- Example: target=4, dice_roll=2 → evidence=`["lower", "half"]`

## Development Practices
- Use conventional commits when committing code to git
- Always use uv and the local venv
- Always use the make file for devops-style tasks

## Architecture
Domain-Driven Design with 3 modules:

1. **Environment Domain** (`domains/environment/environment_domain.py`)
   - EnvironmentEvidence dataclass (contains dice_roll AND comparison_results)
   - Environment class for target/evidence generation with configurable evidence types
   - **ACCESS**: Full knowledge of dice rolls and target values

2. **Belief Domain** (`domains/belief/belief_domain.py`)
   - BeliefUpdate dataclass (contains ONLY comparison_results as List[str])
   - BayesianBeliefState class for inference with multi-evidence support
   - **ACCESS**: NO knowledge of dice roll values or true target
   - **CONSTRAINT**: Must calculate P(comparison_results | target) probabilistically for multiple evidence types

3. **Game Coordination** (`domains/coordination/game_coordination.py`)
   - GameState dataclass (tracks full game state)
   - BayesianGame orchestration class
   - **RESPONSIBILITY**: Filters EnvironmentEvidence to create BeliefUpdate

## Development Commands
- Test: `python -m pytest tests/`
- Run: `python app.py`

## Folder Structure
```
bayesian_game/
├── domains/
│   ├── environment/environment_domain.py
│   ├── belief/belief_domain.py
│   └── coordination/game_coordination.py
├── ui/gradio_interface.py
├── tests/
├── app.py              # Hugging Face entry point
├── requirements.txt
└── CLAUDE.md
```

## Implementation Status
- ✅ Architecture implemented with proper domain separation
- ✅ Domain-driven design with information filtering enforced
- ✅ Gradio UI with graceful completion and comprehensive final results
- ✅ Comprehensive test suite (78 tests) ensuring architectural constraints
- ✅ Proper Bayesian inference without dice roll knowledge
- ✅ Memory leak prevention in matplotlib figure generation

## Key Design Decisions & Architectural Constraints

### Information Flow Rules
1. **Environment → Coordination**: EnvironmentEvidence (dice_roll + comparison_results)
2. **Coordination → Belief**: BeliefUpdate (comparison_results ONLY as List[str])
3. **NEVER**: Direct Environment → Belief communication
4. **NEVER**: Belief domain access to dice roll values

### Multi-Evidence Processing
- Environment generates all applicable evidence types for each roll
- Coordination filters dice_roll information before passing to belief domain
- Belief domain calculates joint probabilities: P(comparison_results | target)
- UI displays evidence configuration options (Basic vs Extended)

### Domain Separation Principles
- **Environment Domain**: No probability knowledge, pure evidence generation
- **Belief Domain**: Pure Bayesian inference, no knowledge of actual dice values
- **Coordination Layer**: Thin orchestration, responsible for information filtering
- **UI Layer**: Separate from core game logic, can display full information

### Critical Implementation Rules
- BeliefUpdate dataclass MUST contain only comparison_results as List[str]
- BayesianBeliefState MUST calculate P(comparison_results | target) probabilistically for multi-evidence
- Game coordination MUST filter dice_roll from EnvironmentEvidence before passing to belief domain
- Tests MUST verify that belief domain never receives dice roll values
- Evidence type configuration MUST be passed through coordination layer, not directly to belief domain

## Maintaining Architectural Integrity

### Code Review Checklist
When modifying the codebase, ensure:
- [ ] BeliefUpdate contains ONLY comparison_results field (List[str])
- [ ] No dice_roll parameter passed to belief domain methods
- [ ] Game coordination filters EnvironmentEvidence properly
- [ ] Tests verify belief domain isolation
- [ ] Belief calculations use probabilistic formulas for multi-evidence: P(comparison_results | target)
- [ ] Evidence type configuration flows through coordination layer
- [ ] UI evidence type selection properly configures game behavior

### Anti-Patterns to Avoid
❌ `BeliefUpdate(dice_roll=X, comparison_results=Y)` - belief shouldn't know dice value
❌ Direct Environment-Belief communication
❌ Belief domain knowing actual dice roll or target values
❌ Hard-coded probability values instead of calculated P(comparison_results | target)
❌ Passing evidence type configuration directly to belief domain

### Correct Patterns
✅ `BeliefUpdate(comparison_results=["lower", "half"])` - only evidence results
✅ Environment → Coordination → Belief information flow
✅ Probabilistic calculations for multi-evidence: P(comparison_results | target)
✅ Evidence type configuration handled in coordination layer
✅ Joint probability calculations: P(["lower", "half"] | target) = P(dice_roll=target/2 AND dice_roll<target)
✅ Clean domain boundaries with no cross-dependencies

## Dependencies
- gradio (for UI)
- numpy (for Bayesian calculations)
- pytest (for testing)
