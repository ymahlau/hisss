# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HISSS (High-Speed Snake Simulator) is a Battlesnake game simulator with a C++ core and Python bindings, designed for AI/RL training. Requires Python >=3.12.

## Commands

### Install / Build
```bash
pip install -e .          # standard install
uv sync --extra dev       # install with all dev dependencies (preferred in CI)
```
The build backend is **scikit-build-core** (`pyproject.toml`). `pip install -e .` triggers a CMake build that compiles the C++ source and links it into a shared library (`liblink.so` / `link.dll` / `liblink.dylib`).

### Run Tests
```bash
pytest                          # all tests
pytest test/game/               # game tests only
pytest test/equilibria/         # Nash equilibrium tests
pytest test/bootcamp/           # environment sanity tests
pytest test/game/test_cpp.py    # single test file
pytest test/game/test_cpp.py::test_name  # single test
```
Tests are written with `unittest.TestCase` but run via pytest.

### Linting / Formatting
```bash
pre-commit run -a               # run all hooks (auto-fixes most issues)
ruff check --fix .              # lint only
ruff format .                   # format only
uvx ty check --error-on-warning # type checking
```
Pre-commit hooks: Ruff (lint + format), `ty` (type checker), zizmor (GitHub Actions security scanner).

## Architecture

The codebase has three layers:

1. **C++ simulation engine** (`src/hisss/cpp/`): Core game logic in `battlesnake.cpp`/`battlesnake_helper.cpp`, Nash solver in `nash.cpp`, and ctypes interface in `link.cpp`. Uses Alglib for linear algebra. Compiled via CMake (`CMakeLists.txt`).

2. **Python ctypes bindings** (`src/hisss/cpp/lib.py`): `CPPLibrary` class loads the compiled shared library and defines all C function signatures using `ctypes` and `np.ctypeslib.ndpointer()`. Accessed globally as `CPP_LIB`. The `Struct` class is an opaque ctypes handle to the C++ `GameState`.

3. **Python API layer** (`src/hisss/game/`): `BattleSnakeGame` wraps a C++ pointer and exposes `reset()`, `step()`, `get_obs()`, `get_state()`, `set_state()`, `render()`. Configuration is done through dataclasses in `config.py`.

### Key Classes and Modules

- `BattleSnakeGame` (`game/battlesnake.py`): Main environment class. Holds a C++ game pointer (`state_p`); all heavy computation happens in C++. **Always call `env.close()` when done** — the C++ object is heap-allocated and must be freed explicitly. `__del__` is a fallback but not guaranteed.
- `BattleSnakeConfig` (`game/config.py`): Dataclass configuring board size, players, food, game mode (wrapped/royale/constrictor/hazards), reward function, and encoding. Preset constructors: `duel_config()`, `standard_config()`, `restricted_duel_config()`, `restricted_standard_config()`.
- `BattleSnakeEncodingConfig` (`game/encoding.py`): Configures observation tensor shape and channel layout. Variants: `Simple`, `Vanilla`, `Best`, `BestRestricted`.
- Reward configs (`game/rewards.py`): `StandardBattleSnakeRewardConfig`, `KillBattleSnakeRewardConfig`, `CooperationBattleSnakeRewardConfig`.
- Nash equilibrium (`equilibria/nash.py`): `calculate_nash_equilibrium()` wraps the C++ solver; falls back to uniform mixing on error.
- `shared.py`: `step_with_draw_prevention()` and `action_kills_player()` utilities used by external agents.
- `encoding_layer_indices()` (exported from `__init__.py`): Returns channel index mapping for observation tensors.

### Build System

The build backend is **scikit-build-core** with CMake (`src/hisss/cpp/CMakeLists.txt`). CMake handles cross-platform compilation with `-O3` (GCC/Clang) or `/O2` (MSVC). The compiled library is loaded by `lib.py` with platform-specific filename detection (`link.dll` / `liblink.dylib` / `liblink.so`).

The legacy shell scripts (`linux_compile.sh`, `windows_compile.bat`) in `src/hisss/cpp/` are not used.
