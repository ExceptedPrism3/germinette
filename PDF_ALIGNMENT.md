# Supplied PDF alignment

Reviewed all pages of the nine PDFs present on 2026-11-05. These local files are
the source of truth for this change; no replacement subjects were downloaded.

| Supplied PDF | Version | Checker | Changes / verification |
| --- | --- | --- | --- |
| `subject module-00.pdf` | 3.0 | `python_module_00` | Function-only structure, exercise directories, arbitrary recursion-helper names, actual recursion, ordered output, authorized builtins/imports, complete seed signature. |
| `subject module-01.pdf` | 3.2 | `python_module_01` | Real main guard, customizable introductory output, required Plant construction, validation/state preservation, protected attributes, vegetable nutrition, mandatory analytics concepts. |
| `subject module-02.pdf` | 3.0 | `python_module_02` | Raised errors rather than silent acceptance, boundary failures recorded, custom default messages, actual watering validation and finally structure; exempt the deliberate operator type error. |
| `subject module-03.pdf` | 3.1 | `python_module_03` | Mixed valid/invalid scores, numeric distance checks and input retries, arbitrary player names, generator production/consumption, two list and two dictionary comprehensions. |
| `subject module-04.pdf` | 3.0 | `python_module_04` | Temporary file probes, full recovered/transformed content, blank lines, replacement and no-save behavior, stdin/stderr routing, string or integer vault action flags, real read/write payloads. |
| `subject module-05.pdf` | 3.1 | `python_module_05` | ABC and processor validation, FIFO order/ranks, polymorphic routing, Protocol plugin dispatch/consumption, valid CSV/JSON export; exempt the guarded invalid-ingestion demonstration. |
| `subject module-05-bis.pdf` | 1.0 | `python_module_05_bis` | Same SHA-256 as the previously audited Codex PDF; preserved the existing remediation and reran its regressions. See `SUBJECT_AUDIT.md`. |
| `subject module-06-bis.pdf` | 1.0 | `python_module_06_bis` | Shared Nexus behavior contracts, annotations/mypy/import policies, distinct factory products, persistent transformations, dedicated invalid-strategy exceptions and call order, executed demonstrations. |
| `subject module-07.pdf` | 3.0 | `python_module_07` | DataDeck factories/capabilities/three strategies, alternative creature names, missing files/package markers, recursive package checks, actual demonstration calls. |

Module detection now recognizes the supplied Module 02/05 filenames and the
root-file Nexus bis layout. Picker labels reflect Module 01 v3.2 and Modules
03/05 v3.1. No dependency was added for these changes.

The DataDeck fixture previously printed example text while its strategies were
no-ops and transformations held no state. It now implements the contracts and
runs actual battles. New Nexus fixtures exercise both supported layouts. Positive
and negative regressions cover the changed contracts and valid alternatives.

This is automated contract coverage, not a complete grading rubric. In particular,
output summaries, custom constructor arguments, statistics internals, dynamic
policy circumvention and conceptual understanding still need peer review. Legacy
checkers continue reporting incomplete outcome accounting. A clean legacy log
therefore does not become a verified JSON pass. The original Codex audit documents
its separate dependency/environment/manual-review boundaries.

Modules 06 (non-bis), 08, 09, 10 and A-Maze-ing have no supplied PDFs in this set.
Their existing regression tests are retained; subject compliance awaits those PDFs.

## Verification

- Python 3.12.15: final complete suite, **173 passed**.
- Python 3.10.22: complete suite before the final malformed-source regression,
  **172 passed**; final Module 05/Nexus regression file, **20 passed**.
- Both full runs emitted the existing Module 09 Pydantic deprecation warning.
- Flake8 passed for the shared contracts, Nexus bis checker, new/rewritten
  regression files and Nexus/DataDeck reference fixtures.
- `git diff --check` passed. Wheel build succeeded and includes both new helpers.
- The code graph was refreshed. Linux and Windows were not executed locally.
