-------- 1.0.14 ------

### Improvements
- **Strict Module 00**: Improved `test_seed_inventory` to detect cases where students print error messages alongside valid output (thanks @eloi-berlinger).

-------- 1.0.13 ------

### Features
- **Strict Docstrings**: Module 01 now strictly enforces docstrings on all classes and methods. Missing docstrings result in an immediate `KO`.
- **Auto-Cleanup**: Germinette now automatically removes `__pycache__` directories after execution to keep your workspace clean.

-------- 1.0.12 ------

### Strictness
- **Single KO Policy**: If `flake8` checks fail, the exercise stops immediately with a single `KO`. Logic tests are skipped to enforce style compliance and avoid confusing "Double KO" outputs.

-------- 1.0.11 ------

### Refinement
- **Silent Linting**: The "Checking Style..." output has been silenced. Style errors are now ONLY shown in the final "Detailed Error Report", preventing "Double KO" confusion.

-------- 1.0.10 ------

### Improvement
- **Cleaner Linting**: `flake8` errors are now grouped in the "Detailed Error Report" at the end, and file paths are hidden to reduce noise.

-------- 1.0.9 ------

### Fix
- **Hotfix**: Fixed `NameError: name 'Panel' is not defined` when reporting linting errors.

-------- 1.0.8 ------

### Feature
- **Linting Support**: Added automatic `flake8` checking for all exercises in Modules 00, 01, and 02. Violations are reported as "Style Errors".

-------- 1.0.7 ------

### Improvement
- **Global Repo Update**: The updater now remembers where you installed Germinette from and updates that git repository regardless of where you run the command from.

-------- 1.0.6 ------

### Feature
- **Smart Repo Update**: `germinette -u` now also updates your local git repository (if you are standing in it).
- **Force Reset**: If git merge conflicts occur, you can interactively choose to force-reset to match the remote.

### Strictness
- **Module 02**: Added strict script execution checks (Example output verification) for all exercises.

-------- 1.0.5 ------

### Fix
- Fixed infinite update loop in `germinette -u` by ensuring update is only run if a new version is actually available.

-------- 1.0.4 ------

### Change
- Restored visual "KO" indicator for failed exercises (was missing in previous refactor).

-------- 1.0.3 ------

### Change
- Updated Module 01 Exercise 6 tester to verify Nested Classes correctly (fixing incorrect strict check for attributes on the main class).
- Removed strict check for `total_gardens` variable in Ex6.

-------- 1.0.2 ------

### Change
- Updated Module 01 Exercise 0 to run as a subprocess script (supports `if __name__ == "__main__":`).
- Updated Module 01 Exercise 2 to accept `get_older` alias for `age_plant`.
- Relaxed Module 01 Exercise 1 `__str__` requirement if not strictly mandated.
- Forced reinstall for environment consistency.

-------- 1.0.1 ------

### Addition
- Added version display to CLI banner.
- Added `--update` / `-u` flag for self-updating.
- Added `install.sh` for one-click installation and PATH fixing.

### Change
- Improved `ModuleNotFoundError` to offer fuzzy suggestions instead of raw dump.

-------- 1.0.0 ------

### Addition
- Initial release of Germinette.
- Support for Module 00 and Module 01.
