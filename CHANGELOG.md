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
