# Changelog

## [1.8.8] - 2026-04-29
### Fixed
- **Auto-detection robustness (file checker hardening)**: Reworked `ModuleDetector.detect()` from first-hit matching to a weighted signature-scoring strategy that prioritizes distinctive required files over generic directory patterns, reducing cross-module false positives in mixed or partially-complete student repositories.
- **Module 07 vs Module 09 collision fix**: Tightened DataDeck signatures by removing generic `ex*/__init__.py` markers from Module 07 detection, preventing Cosmic Data (`ex0/space_station.py`, `ex1/alien_contact.py`, `ex2/space_crew.py`) workspaces from being misclassified as Module 07.
- **Root regression coverage for module detection**: Added `tests/test_module_detector_alignment.py` cases to lock Module 09 detection behavior against Module 07 signature collisions and future detector regressions.

## [1.8.7] - 2026-04-28
### Fixed
- **A-Maze-ing v2.1 lint-rule parity**: Hardened `a_maze_ing` Makefile validation so the mandatory `lint` recipe now enforces the required mypy flags from the subject (`--warn-return-any`, `--warn-unused-ignores`, `--ignore-missing-imports`, `--disallow-untyped-defs`, `--check-untyped-defs`) instead of only checking for generic `mypy` presence.
- **A-Maze-ing v2.1 “42” pattern enforcement**: Added explicit output-grid validation for the required visible `"42"` built from fully closed cells (`0xF`), while preserving subject-compliant small-maze behavior by requiring an explanatory runtime message when the pattern is omitted due to size constraints.
- **Root regression coverage for A-Maze-ing checker alignment**: Added `tests/test_a_maze_ing_checker_alignment.py` to lock Makefile lint-flag enforcement and `"42"` requirement behavior (including small-maze exemption messaging) against future regressions.

## [1.8.6] - 2026-04-28
### Fixed
- **Module 07 auto-detection reliability**: Updated `ModuleDetector` DataDeck signatures to match v3.0 layouts (`battle.py`, `capacitor.py`, `tournament.py` plus `ex0/`, `ex1/`, `ex2/` package markers), so `germinette` now auto-detects Module 07 correctly from standard project folders.
- **Module 08 builtin `types` allowance**: Adjusted Matrix checker import policy to accept the stdlib `types` module in Ex0/Ex1/Ex2 strict checks when students use it.
- **Module 06 v2.0 parity completion**: Added two missing codex rules in checker logic: (1) preserve the intentional pedagogical mypy exception path for `ft_alembic_4.py`, and (2) require `alchemy/transmutation/recipes.py` to include at least one absolute import and one relative import, as demanded by Part III.
- **Module 06 regression expansion**: Extended `tests/test_module06_v20_alignment.py` with coverage for the Alembic 4 mypy-exception allowance and transmutation import-style enforcement.
- **Module 09 v3.0 checker hardening**: Tightened Cosmic Data validation by enforcing required `ex0`/`ex1`/`ex2` file presence, strengthening field-constraint checks in Ex0, and adding Pydantic v2 validation expectations (reject deprecated `@validator`, require `@model_validator` for business-rule exercises).
- **Root regression coverage for Module 09 checker**: Added `tests/test_module09_v30_alignment.py` to lock project-structure checks and Pydantic validator-policy behavior.
- **Module 10 v3.0 checker hardening**: Strengthened FuncMage validation by adding explicit forbidden checks for `eval()`/`exec()`, module-level global variable detection, stricter external-import rejection, stricter lambda enforcement for Exercise 0, and tighter Exercise 1 behavior checks using the documented `(target, power)` higher-order contracts.
- **Root regression coverage for Module 10 checker**: Added `tests/test_module10_v30_alignment.py` to lock forbidden-function/global-state behavior and higher-order signature flow checks.
- **Module 00 v3.0 checker hardening**: Added AST-level structure enforcement for Growing Code submissions, including no top-level executable statements, no `if __name__ == "__main__":` blocks, and “only requested function per file” checks, with a dedicated recursive helper allowance for Ex6 recursive implementation.
- **Root regression coverage for Module 00 checker**: Added `tests/test_module00_v30_alignment.py` to lock `__main__`-block rejection and Ex6 recursive helper acceptance behavior.
- **Root regression coverage for Module 01 checker**: Added `tests/test_module01_v30_alignment.py` to lock key Module 01 expectations (Ex0 main-guard requirement and Ex1 `Plant.show()` requirement) against future checker drift.

## [1.8.5] - 2026-04-27
### Fixed
- **Module 05 v3.0 checker alignment**: Updated `python_module_05` strict checks to match Code Nexus v3.0 general rules (imports restricted to `abc`/`typing`, all builtins authorized) and removed the non-subject `super()` mandate that caused false negatives.
- **Module 05 structure validation refresh**: Added targeted AST checks for required architecture elements: Ex0 class/method contracts (`DataProcessor` + `validate`/`ingest`/`output`), Ex1 `DataStream` required methods (`register_processor`, `process_stream`, `print_processors_stats`), and Ex2 `ExportPlugin` protocol flow plus `output_pipeline` and CSV/JSON plugin presence.
- **Module 05 runtime expectation cleanup**: Replaced legacy hardcoded output markers with v3.0-oriented markers that preserve flexibility allowed by the subject examples while still validating mandatory pipeline demonstration sections.
- **Root regression coverage for Module 05 checker**: Added `tests/test_module05_v30_alignment.py` to lock these v3.0 expectations and reduce future checker drift.
- **Module 06 v2.0 checker hardening**: Strengthened The Codex checks by enforcing project-local import rules (rejecting out-of-project imports), preserving forbidden `eval()` / `exec()` and `sys.path` protections, and adding mandatory laboratory tree validation against the expected module/package layout.
- **Root regression coverage for Module 06 checker**: Added `tests/test_module06_v20_alignment.py` to lock import-scope and required-structure behavior, reducing future drift in Module 06 validation.
- **Module 07 v3.0 checker hardening**: Tightened DataDeck checks to enforce module-local import policy (external libraries forbidden), align builtin authorization with subject rules (`eval`/`exec` excluded), and require mandatory `__init__.py` package files in `ex0/`, `ex1/`, and `ex2/`.
- **Root regression coverage for Module 07 checker**: Added `tests/test_module07_v30_alignment.py` to lock external-import rejection and required package-init enforcement for Module 07.
- **Module 07 auto-detection fix**: Updated `ModuleDetector` signatures for DataDeck v3.0 so standard layouts (`battle.py`, `capacitor.py`, `tournament.py` + `ex0/`/`ex1/`/`ex2/`) are correctly auto-detected when running `germinette` from module folders.

## [1.8.4] - 2026-04-27
### Fixed
- **Module 04 v3.0 checker realignment**: Corrected subject drift in `python_module_04` by enforcing the right Exercise 1 header (`=== Cyber Archives Recovery & Preservation ===`), validating line-end `#` transformation (instead of legacy comment-prefix checks), and replacing the off-subject Exercise 2 stream scenario with v3.0 recovery/preservation flow checks (`sys.stdin` input path + `[STDERR]`-prefixed error routing).
- **Module 04 structure/contract enforcement**: Added explicit pre-Ex3 guard forbidding `with` usage in Exercises 0-2, aligned allowed imports with `typing`-annotated subject expectations, and strengthened Exercise 3 verification to validate `secure_archive()` behavior as a real `(bool, str)` contract for read/write and error cases.
- **Root regression coverage for Module 04 checker**: Added `tests/test_module04_v30_alignment.py` to lock these v3.0 expectations and reduce future false positives/false negatives.

## [1.8.3] - 2026-04-27
### Fixed
- **Module 08 v3.0 checker compliance hardening**: Aligned `python_module_08` checks with subject expectations across all exercises. Ex0 now validates mandatory matrix/venv markers and mode-specific guidance/details; Ex1 now enforces required dependency artifacts (`requirements.txt` + `pyproject.toml`), numpy-driven dataset intent, and explicit pip/Poetry comparison while allowing only import-related style/type noise as permitted by the subject; Ex2 now enforces required `.env.example` keys (`MATRIX_MODE`, `DATABASE_URL`, `API_KEY`, `LOG_LEVEL`, `ZION_ENDPOINT`) plus visible dev/prod output differences through environment-driven runs.
- **Root regression coverage for Module 08 checker**: Added `tests/test_module08_v30_alignment.py` to lock the updated v3.0 behavior and prevent reintroduction of partial or legacy checks.

## [1.8.2] - 2026-04-24
### Fixed
- **Module 03 Ex3 (Achievement Hunter) v3.0 checker** ([#14](https://github.com/ExceptedPrism3/germinette/issues/14), reported by **koldoest26**): `ft_achievement_tracker` is now validated against **Data Quest v3.0** (four players Alice–Dylan, `All distinct achievements:` / `Common achievements:` / `Only <name> has:` / `<name> is missing:`) instead of legacy phrases (`Common to all players:`, `Total unique achievements:`, etc.). Stricter import list for this exercise now matches the subject (only `random`, not `sys`).

## [1.8.1] - 2026-04-23
### Fixed
- **Module 03 v3.0 checker alignment** ([#13](https://github.com/ExceptedPrism3/germinette/issues/13), reported by **koldoest26**): Updated Data Quest checks to match subject v3.0 by allowing `round()` in Ex2, requiring the Ex4 header `=== Inventory System Analysis ===`, replacing outdated Ex5 damage/items expectations with player-action stream validation, and allowing `random` + list/dict comprehension validation flow in Ex6.

## [1.8.0] - 2026-04-22
### Added
- **A-Maze-ing checker (subject-aligned)**: Added full `germinette/subjects/a_maze_ing.py` coverage for mandatory files, Makefile targets, config parsing, README requirements, reusable `mazegen` packaging checks, runtime/output format validation, wall-coherence checks, border-wall checks, 3x3-open-area prevention checks, shortest-path validation, and `PERFECT=True` tree validation on the traversable component.
- **A-Maze-ing seed safety checks**: Added explicit checks for deterministic behavior when `SEED` is missing/commented, variability when `SEED` is present, and AST-based detection of broken interactive regen logic (`R`) plus invalid `launch(seed=...)` forwarding.
- **Root test coverage for A-Maze-ing checker**: Added `tests/test_a_maze_ing_checker_seed_logic.py` so seed-logic regressions are tested from the main repository test suite.

### Changed
- **Module menu and version labeling**: `a_maze_ing` is now listed as fully available in the module picker and labeled with PDF-derived version `v.2.1`.
- **A-Maze-ing warning UX**: Improved warning section readability and clarified that warnings are non-blocking.
- **A-Maze-ing package artifact detection**: Checker now accepts real-world `mazegen` artifact names using both hyphen and underscore prefixes (e.g. `mazegen_sabo_gla_bgebreeg-*.whl`).

### Fixed
- **A-Maze-ing sample project seed forwarding** (`devtools/other/amazing_sabo`): Restored correct UI seed forwarding (`launch(seed=seed)`) so commented/missing `SEED` does not accidentally enable seed increment behavior on regenerate.

## [1.7.1] - 2026-04-21
### Added
- **Subject version sync tooling**: Added `scripts/check_subject_updates.py` and `scripts/subject_pdf_urls.json` to compare Module 00-10 subject `Version:` values from official CDN PDFs against `MODULE_VERSION_LABELS`.
- **Module 02 stricter pedagogical checks** ([#12](https://github.com/ExceptedPrism3/germinette/issues/12), reported by **bgebreeg**): Enforced exception-handling location in Ex0, required natural exception-triggering code + multi-exception tuple handling in Ex2, and enforced one global `try/except/finally` flow with immediate return on error in Ex4.
- **Module 01 runtime-sanity checks** ([#11](https://github.com/ExceptedPrism3/germinette/issues/11), reported by **muali**): Added static checks for suspicious builtin misuse in `super().__init__(...)` and undefined `self.<attr>` access patterns (with inheritance-aware safeguards).

### Changed
- **Global style gate**: `BaseTester.check_flake8()` now runs both `flake8` and `mypy`, and reports failures from either checker in one combined diagnostics block.
- **Module menu labeling**: Module picker shows per-module version suffixes via `MODULE_VERSION_LABELS` and formatting helper.

### Fixed
- **Module 00/01 v3.0 alignment**: Restored subject-correct exercise mapping (`ft_garden_name` in Mod00 Ex1, strict `show()` expectation in Mod01 Ex1, and minimum plant-output expectations per subject).
- **A-Maze-ing project robustness** (`devtools/other/amazing_sabo`): Updated non-perfect wall-breaking to prevent creation of forbidden 3x3 fully-open areas while preserving loop generation.
- **Dev fixtures cleanup and alignment**: Reworked `devtools/test` fixtures for Modules 00, 01, and 02 to match current v3.0 subjects; removed stale shifted files and debug artifacts.
- **mypy-compatible dev fixtures**: Updated affected fixture files in Modules 02/03/08/10 to pass the new combined `flake8 + mypy` enforcement.

## [1.7.0] - 2026-04-06
### Added
- **Global v3.0 Compatibility**: Core updater logic (`MODULE_VERSION_LABELS`) properly aligns Module 00 through Module 10 to standard v3.0 specs.
- **Module 02**: Added tests parsing behavior and error handling of `ft_raise_exception` and native core Exceptions like `TypeError`.
- **Module 03**: Abstract Syntax Tree parsing ensuring `ft_data_alchemist` specifically utilizes List Comprehensions per v3.0 rubric.
- **Module 04**: Comprehensive tests for handling `sys.stdin`/`sys.stderr` safely (added string checks for exact validation brackets e.g. `[STDERR]`).
- **Module 05 Code Nexus**: Completely new evaluation path tailored to test Abstract Base Classes (`data_processor`), multi-faceted inheritance Polymorphism (`data_stream`), and Python Protocols (`data_pipeline`).
- **Module 06 The Codex**: Full overwrite matching the massive v2.0 package integration refractor: enforces execution validation, circular dependencies, absolute/relative routing, and package visibility mapping.
- **Module 07 DataDeck**: Dropped the old Card format logic and rewrote tests checking for `CreatureFactory` (Abstract Factory mapping), `HealCapability` (Mixins), and `BattleStrategy` (Abstract Strategy).
- Modules 08, 09, and 10 required zero evaluation overwrites (only simple version bumps) and remain fully compliant natively.

### Removed
- **Legacy Logic**: Hundreds of lines of deprecated code wiped relating to dead v1.0 and v2.0 exercises (`ft_analytics_dashboard`, `ft_crisis_response`, old card games, etc.).

## [1.6.11] - 2026-03-24
### Fixed
- **`install.sh` (`--home`)**: On **uv-managed Python**, `python3 -m venv` often fails (`ensurepip` error) leaving a broken `.germinenv`. The script now removes incomplete envs, prefers **`uv venv .germinenv`** when `uv` is on `PATH`, installs with **`uv pip install --python …`** or the venv interpreter directly (no `source activate`, so the system `python3` is never used for `pip install`).

## [1.6.10] - 2026-03-24
### Fixed
- **`install.sh`**: On **PEP 668** / externally managed Python (including **uv**-managed interpreters), automatically fall back to an isolated `.germinenv` install (same as `--home`) instead of failing on `pip install --user`. Secondary retry if pip errors mention `externally-managed-environment` but the marker file was missed.

## [1.6.9] - 2026-03-23
### Fixed
- **Strict imports**: `typing_extensions` is allowed alongside `typing` in `check_imports` (e.g. `Self` on Python 3.10; Issue **#10**, thanks **@mauricelorenz**).

## [1.6.8] - 2026-03-19
### Added
- **Integration tests**: Golden reference project for Module 07 under `tests/fixtures/python_module_07_golden/` and `tests/test_integration_module07.py`.
- **CI**: GitHub Actions workflow (`.github/workflows/ci.yml`) runs Module 07 integration tests on Python 3.10 and 3.12.
- **Developer install**: `pip install -e ".[dev]"` extra in `setup.py` (includes `pytest`).

### Fixed
- **`install.sh`**: If `pip` exits non-zero after a successful install (e.g. **pyenv** cannot rehash shims), verify the package and continue with a warning instead of failing (Issue **#9**, thanks **@GayaOliveira**).
- **`germinette.core`**: `check_imports` now allows `from __future__ import annotations` (standard library).
- **Module 06**: `ft_pathway_debate` output check accepts longer `philosophers_stone()` lines and typographic apostrophes (Issue **#8**, thanks **@IntRogerYT**).

### Changed
- **Module 07 tester**: Repository root `__init__.py` is required (recorded error, not only a warning); flake8/type-hint/strict checks run on all primary `.py` files per exercise (including `main.py`, `__init__.py`, Ex1 `SpellCard`/`ArtifactCard`, Ex2 `Combatable`/`Magical`, etc.).
- **README**: Maintainer section for integration tests; Conda/venv `python` vs `pip` troubleshooting; **version & update** block at the end of the file.
- **CLI**: Footer order: (if **no errors**) green **“All exercises passed”** panel → red **Disclaimer** → **version** / update line last. Unknown `-e` / exercise name now records an error so a false “all passed” is not shown. **A-Maze-ing** KO paths now use `record_error` + grouped report.
- **CLI**: End-of-run footer uses GitHub `main` to decide: **yellow “update available” panel** only when a newer version exists; otherwise a dim **“up to date”** line (or offline hint). `check_update()` now returns `(needs_update, remote_version, check_ok)`; `germinette -u` no longer claims “latest” when the version check failed (e.g. offline).

### Fixed (follow-up)
- **Module 03 Exercise 4** (`ft_inventory_system`): authorized **`sum`**, **`max`**, **`min`**, **`list`** alongside dict-centric builtins for typical inventory reports.

### Notes (tester alignment, earlier in this release cycle)
- Stricter alignment with subjects across modules **00–10** (e.g. type hints / flake8 where required, Module 09 Pydantic rules, Module 03 Ex5 imports, Module 00 plant-age boundary, Module 01 CodeCultivation checks and banner).

## [1.6.5] - 2026-02-07
### Fixed
- **Installation**: `install.sh` now detects active virtual environments (`$VIRTUAL_ENV`) and installs without `--user` flag to avoid errors (Issue #6).

## [1.6.4] - 2026-02-05
### Added
- **Infrastructure**: Added `--home` flag to `install.sh` (Feature #4).
  - Creates and installs into a local virtual environment (`.germinenv`).
  - Automatically symlinks the binary to `~/.local/bin/germinette`.
  - Bypasses PEP 668 restrictions on managed systems.

## [1.6.3] - 2026-02-05
### Fixed
- **Module 03**: Updated `ft_inventory_system` (Ex4) tester to match Version 2.2 Subject (Issue #5).
  - New output requirements (Analysis, Categories, Suggestions).
  - Removed outdated gold/transaction checks.

## [1.6.2] - 2026-02-03
### Changed
- **Module 01**: Relaxed verify strictness based on subject re-eval.
  - Ex2: Removed strict check for `grow()` method name.
  - Ex3: Removed minimum instance count check (5).
  - Ex4: Removed valid accessor checks for `get_height` and `get_age`.
  - Ex5: Removed strict check for `bloom()` method.
  - Ex6: Removed strict check for specific analytics output strings.

## [1.6.1] - 2026-02-03
### Fixed
- **Module 10**:
  - Authorized `round()` function (required for Ex0).
  - Fixed missing type hints in solution files (inner functions, test helpers).

## [1.6.0] - 2026-02-03
### Added
- **Module 10: FuncMage (Functional Programming)**:
  - Added support for all Functional Programming exercises.
  - Ex0: Lambda Sanctum (`lambda_spells.py`).
  - Ex1: Higher Realm (`higher_magic.py`).
  - Ex2: Memory Depths (`scope_mysteries.py`).
  - Ex3: Ancient Library (`functools_artifacts.py`).
  - Ex4: Master's Tower (`decorator_mastery.py`).
- **Features**:
  - Validates usage of functional patterns (lambdas, closures, decorators).
  - Enforces strict type hints (including return types).
  - Forbids classes in Ex0-Ex3 (Functional focus).

## [1.5.7] - 2026-01-30
### Fixed
- **Module 08 & 09**:
  - Enforced strict type hint checking (including return types) as per requirements.

## [1.5.6] - 2026-01-30
### Added
- **Module 09**: Initial release with Pydantic support.
    - Ex0: `SpaceStation` model.
    - Ex1: `AlienContact` model.
    - Ex2: `SpaceMission` model.

### Changed
- **Global**: Removed mandatory docstring checks from Modules 01, 03, 04, 05, and 06.
  - Aligns with the non-mandatory nature of docstrings in these subjects.

## [1.5.5] - 2026-01-29


### Changed
- **Module 02**: Removed mandatory docstring checks.

## [1.5.4] - 2026-01-29
### Changed
- **Module 08**:
    - Authorized `site` module in `common_strict_check` for virtual environment operations.

## [1.5.3] - 2026-01-28
### Fixed
- **Module 01**:
    - Moved `get_info()` check from Exercise 1 to Exercise 2, matching the correction sheet requirements.

## [1.5.2] - 2026-01-28
### Refactored
- **Module 08**:
    - Removed hardcoded test bypasses in solution files.
    - Cleaned up comments to ensure solutions look authentic.
    - Verified solutions against real dependencies (`pandas`, `numpy`, etc.).

## [1.5.1] - 2026-01-28
### Fixed
- **Module 08**:
    - Fixed `flake8` violations in solution files (`construct.py`, `loading.py`, `oracle.py`).
    - Corrected line lengths, whitespace, and formatting issues.

## [1.5.0] - 2026-01-28
### Added
- **Module 08: The Matrix (Environment & Config)**
  - Implemented `python_module_08` tester.
  - Added support for Exercise 0 (`construct.py` - Virtual Env detection).
  - Added support for Exercise 1 (`loading.py` - Dependency Management).
  - Added support for Exercise 2 (`oracle.py` - Environment Variables).
  - Added solution files in `devtools/test/python_module_08`.

## [1.4.3] - 2026-01-28
### Fixed
- **Module 07 Verification**:
  - Corrected output expectations for dictionary printing (added spaces).
  - Fixed strictness checks to allow relative imports (e.g., `from ex0.Card import Card`).
  - Relaxed strictness on library files (disabled mandatory `try/except` check for non-main files).
  - Enabled auto-detection for `python_module_07`.

## [1.4.2] - 2026-01-27
### Added
- **Module 07: DataDeck (Abstract Base Classes)**
    - Implemented strictness checks for ABC usage, multiple inheritance, and design patterns.
    - Verified output against `en.subject-25.pdf`.

## v1.4.1 - PDF Sync Update (2025-01-25)
- **Mod 04 Update (v23 PDF)**:
  - Updated content checks for "Ancient Text" and "Crisis Response" to match v23 strings.
  - Enforced strict authorization for `open` usage (skipped if not strictly authorized).
  - Simulate real crisis constraints (chmod 000 for vault test).
- **Mod 05 Update (v24 PDF)**:
  - Strict output matching for Polymorphic Streams ("Pipeline capacity" etc.).
  - Enforced strict function allow-lists (`super`, `isinstance` mandatory).
  - Clarified authorized imports (`random`, `time`, `collections` for specific exercises).

## v1.4.0 - Strictness Standardization (2025-01-24)
- **Mod 03 Complete**: Fully enforced v22 PDF strictness (Removed `sorted`, `list`, `enumerate`. Only `sys` imported).
- **Global Strictness**: Refactored `BaseTester` to handle strict authorized function checks and imports centrally.
- **Mod 05 & 06 Upgrade**: Updated both modules to use the new strictness engine.
  - Mod 05 now strictly checks for `super()` and authorized functions (`zip`, `sum`, etc. allowed).
  - Mod 06 now strictly whitelists `alchemy` and `sys` imports while banning magic like `importlib`.
- **Cleanup**: Tidy up of codebase and removal of debug artifacts.

## v1.3.5 - Module 06 "The Codex"
- **New Module**: Added support for Module 06 (Import Mysteries).
- **Features**:
  - Checks for package exposure (`ft_sacred_scroll`).
  - Verifies import transmutation (aliasing, specific imports).
  - Handles circular dependency checks (`ft_circular_curse`).
- **Safety**: Added checks to forbid `sys.path` hacking and `exec`/`eval`.

## v1.3.3 - Module 02 Strictness Update
- **Feature**: Strict implementation of "Authorized Functions" for Module 02.
- **Strictness**: Mandatory `try/except` enforcement across all exercises.
- **Fixes**: Corrected function signature checks in `ft_garden_management`.

## v1.3.0 - Module 05 "Code Nexus" & Module 04 "Data Archivist"
- **New Modules**: Added full test suites for Module 04 and Module 05.
- **Module 05**:
  - Protocol & ABC verification.
  - Polymorphism output matching (Data Processor, Stream Nexus).
- **Module 04**:
  - Context Manager checks (`with` statement).
  - File I/O verification (creating archives, reading logs).
- **Enhancement**: Added "Single KO" policy - testing stops at the first failure to save time.

## v1.2.0 - Core Improvements
- **UI**: Better error grouping and clearer "Exercise X" titles.
- **Update System**: `germinette -u` command to auto-update the tool.

---
*Older versions omitted for brevity.*
