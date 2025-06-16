# Bayesian Game Project

## Project Overview
A Bayesian Game implementation featuring a Belief-based Agent using domain-driven design.

## Game Rules
- Judge and Player 1 can see the target die value
- Player 2 must deduce the target value using only comparison results
- Player 1 rolls dice and reports "higher"/"lower"/"same" compared to target
- **CRITICAL**: Player 2 receives ONLY the comparison result, NOT the dice roll value
- Game runs for 10 rounds
- Judge ensures truth-telling

## Development Practices
- Use conventional commits when committing code to git

## Architecture
Domain-Driven Design with 3 modules:

1. **Environment Domain** (`domains/environment/environment_domain.py`)
   - EnvironmentEvidence dataclass (contains dice_roll AND comparison_result)
   - Environment class for target/evidence generation
   - **ACCESS**: Full knowledge of dice rolls and target values

2. **Belief Domain** (`domains/belief/belief_domain.py`)
   - BeliefUpdate dataclass (contains ONLY comparison_result)
   - BayesianBeliefState class for inference
   - **ACCESS**: NO knowledge of dice roll values or true target
   - **CONSTRAINT**: Must calculate P(comparison_result | target) probabilistically

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
1. **Environment → Coordination**: EnvironmentEvidence (dice_roll + comparison_result)
2. **Coordination → Belief**: BeliefUpdate (comparison_result ONLY)
3. **NEVER**: Direct Environment → Belief communication
4. **NEVER**: Belief domain access to dice roll values

### Domain Separation Principles
- **Environment Domain**: No probability knowledge, pure evidence generation
- **Belief Domain**: Pure Bayesian inference, no knowledge of actual dice values
- **Coordination Layer**: Thin orchestration, responsible for information filtering
- **UI Layer**: Separate from core game logic, can display full information

### Critical Implementation Rules
- BeliefUpdate dataclass MUST contain only comparison_result
- BayesianBeliefState MUST calculate P(comparison_result | target) probabilistically
- Game coordination MUST filter dice_roll from EnvironmentEvidence before passing to belief domain
- Tests MUST verify that belief domain never receives dice roll values

## Maintaining Architectural Integrity

### Code Review Checklist
When modifying the codebase, ensure:
- [ ] BeliefUpdate contains ONLY comparison_result field
- [ ] No dice_roll parameter passed to belief domain methods
- [ ] Game coordination filters EnvironmentEvidence properly
- [ ] Tests verify belief domain isolation
- [ ] Belief calculations use probabilistic formulas, not direct dice values

### Anti-Patterns to Avoid
❌ `BeliefUpdate(dice_roll=X, comparison_result=Y)` - belief shouldn't know dice value
❌ Direct Environment-Belief communication
❌ Belief domain knowing actual dice roll or target values
❌ Hard-coded probability values instead of calculated P(comparison_result | target)

### Correct Patterns
✅ `BeliefUpdate(comparison_result="higher")` - only comparison result
✅ Environment → Coordination → Belief information flow
✅ Probabilistic calculations: P(roll > target) = (dice_sides - target) / dice_sides
✅ Clean domain boundaries with no cross-dependencies

## Dependencies
- gradio (for UI)
- numpy (for Bayesian calculations)
- pytest (for testing)