# Changelog

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
