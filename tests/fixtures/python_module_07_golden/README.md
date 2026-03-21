# Module 07 (DataDeck) golden reference

Minimal **ex0–ex4** tree used by `tests/test_integration_module07.py` to verify that
`germinette/subjects/python_module_07.py` still passes a known-good project (flake8,
type hints, `verify_strict`, and expected stdout).

- Run from repo root: `python -m pytest tests/test_integration_module07.py -v`
- Same layout students use: repo root `__init__.py`, then `ex0/` … `ex4/` with
  `main.py` runnable as `python3 -m exN.main`.

This is **not** an official 42 solution—only a regression harness for the tester.
