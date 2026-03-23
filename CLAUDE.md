# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HISSS (High-Speed Snake Simulator) is a Battlesnake game simulator with a C++ core and Python bindings, designed for AI/RL training.

## Commands

### Install / Build
```bash
pip install -e .
```
This compiles the C++ shared library (`src/hisss/cpp/compiled/liblink.so`) via the custom Hatchling hook in `hatch_build.py`.

### Run Tests
```bash
pytest                          # all tests
pytest test/game/               # game tests only
pytest test/equilibria/         # Nash equilibrium tests
pytest test/bootcamp/           # environment sanity tests
pytest test/game/test_cpp.py    # single test file
pytest test/game/test_cpp.py::test_name  # single test
```

## Architecture

The codebase has three layers:

1. **C++ simulation engine** (`src/hisss/cpp/`): Core game logic in `battlesnake.cpp`/`battlesnake_helper.cpp`, Nash solver in `nash.cpp`, and ctypes interface in `link.cpp`. Uses Alglib for linear algebra. Compiled to `liblink.so`.

2. **Python ctypes bindings** (`src/hisss/cpp/lib.py`): `CPPLibrary` class loads `liblink.so` and defines all C function signatures. Accessed globally as `CPP_LIB`.

3. **Python API layer** (`src/hisss/game/`): `BattleSnakeGame` wraps a C++ pointer and exposes `reset()`, `step()`, `get_obs()`, `get_state()`, `set_state()`, `render()`. Configuration is done through dataclasses in `config.py`.

### Key Classes and Modules

- `BattleSnakeGame` (`game/battlesnake.py`): Main environment class. Holds a C++ game pointer; all heavy computation happens in C++.
- `BattleSnakeConfig` (`game/config.py`): Dataclass configuring board size, players, food, game mode (wrapped/royale/constrictor/hazards), reward function, and encoding. Preset constructors: `duel_config()`, `standard_config()`, `restricted_duel_config()`, `restricted_standard_config()`.
- `BattleSnakeEncodingConfig` (`game/encoding.py`): Configures observation tensor shape and channel layout. Variants: `Simple`, `Vanilla`, `Best`, `BestRestricted`.
- Reward configs (`game/rewards.py`): `StandardBattleSnakeRewardConfig`, `KillBattleSnakeRewardConfig`, `CooperationBattleSnakeRewardConfig`.
- Nash equilibrium (`equilibria/nash.py`): `calculate_nash_equilibrium()` wraps the C++ solver; falls back to uniform mixing on error.
- `shared.py`: `step_with_draw_prevention()` and `action_kills_player()` utilities used by external agents.

### Build System

`hatch_build.py` is a custom Hatchling build hook. On `pip install` it:
1. Compiles Alglib `.cpp` files
2. Compiles project source files
3. Links everything into `liblink.so`

It uses incremental compilation (skips files where `.o` is newer than source). Compiler flags: `g++ -Wall -std=c++11 -O3 -fPIC`.

The `CMakeLists.txt` and shell scripts (`linux_compile.sh`, `windows_compile.bat`) in `src/hisss/cpp/` are legacy and not used by the standard build.
