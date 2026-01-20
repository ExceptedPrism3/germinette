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
