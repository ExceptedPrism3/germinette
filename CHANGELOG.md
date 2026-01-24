
# Changelog

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
