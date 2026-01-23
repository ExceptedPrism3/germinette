# Changelog

## v1.3.3 - Module 02 Strictness Update (2025-??-??)
- **Feature**: Implemented Strict/Authorized Function Checks for Module 02 "Garden Guardian" (v21 PDF).
- **Strictness**:
  - Enforced usage of "Authorized Functions" only (using AST analysis).
  - Enforced mandatory `try/except` blocks in all exercises.
- **Bug Fix**: Fixed missing test function in Mod 02 Ex5 (`check_authorized_functions` was missing).
- **Maintenance**: Updated `ft_garden_management.py` to match new strict requirements.
# Changelog

## v1.3.2 - Module 06 "The Codex" (2025-??-??)
- **New Feature**: Implemented support for Module 06 "Import Mysteries".
- **Tests Added**:
    - `ft_sacred_scroll`: Checks for proper package `__init__.py` exposure.
    - `ft_import_transmutation`: Verifies various import styles (aliased, specific, etc.).
    - `ft_pathway_debate`: Verifies absolute vs relative imports.
    - `ft_circular_curse`: Verifies resolution of circular dependencies (Late Imports).
- **Strict Checks**:
    - Enforced prohibition of `sys.path`, `importlib`, `exec`, `eval` using AST analysis.
    - Enforced `try/except` for robust error handling.
- **Bug Fix**: Added missing `_load_module` and `record_error` helper methods to `python_module_06.py`.

# Changelog

## v1.3.1 (2026-01-20)
- **Fix**: Strict enforcement of **PDF requirements** for Module 05.
  - Added AST-based checks for `super()` usage in constructors.
  - Added checks for `try/except` blocks in solution files.
  - Refactored `devtools` solutions to strictly follow structural requirements (inheritance, error handling).
- **Style**: Fixed Flake8 line length violations in Module 05 solutions.

## v1.3.0 (2026-01-20)
- **Feature**: Implemented **Module 05: Code Nexus (Polymorphism)** support.
  - Added strict tests for `stream_processor.py` (Ex0), `data_stream.py` (Ex1), and `nexus_pipeline.py` (Ex2).
  - Enforced ABC inheritance, Protocol usage, and complex output formatting.
  - Verified against PDF v19 requirements ("Authorized: isinstance, print, collections").
- **Core**: Updated `ModuleDetector` and `Runner` to support Module 05 file structure.
- **Fix**: Removed Module 05 from "Coming Soon" list.

## v1.2.5 (2026-01-20)
<truncated>
