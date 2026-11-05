# Attached subject PDF: complete checker audit

Audit date: 2026-11-05. Repository revision:
`2b7657a52dce3882dc23bc6a7d401d2b1a04c97c`.

**This is the original audit of the revision above. The rework on this branch is
described in the remediation section at the end; the findings below preserve
the evidence of the original behavior.**

**Verdict: the checker only partially covers this subject. A deliberately broken
submission passed all 39 recorded checks, with no failures, errors, or skips.**
The regression suite passes after adding an undeclared test dependency, but that
does not establish subject compliance.

## Source and scope

The attached [subject.pdf](subject.pdf) is **The Codex — Packages, Environments
and the Alchemist's Toolchain, version 1.0**, not version 3.1. Its SHA-256 is
`34532cd1334187f60c77f1b0fd00f804791fd3c7d1d6c8882d17e62f5a96617d`.
The user confirmed that this attached PDF is the source of truth. No version 3.1
PDF was supplied or audited. Page references below use the printed page numbers;
the physical PDF page number is one higher because of the cover.

All 23 PDF pages were extracted and read. The matching implementation is
[python_module_05_bis.py](germinette/subjects/python_module_05_bis.py), not the
older `python_module_06` Codex checker. The audit follows all five exercises,
[bis_common.py](germinette/subjects/bis_common.py), module detection, runner and
CLI reporting, documentation, CI configuration, and every regression test's
applicability to this PDF. Other modules lack their corresponding PDFs here, so
their subject compliance cannot be established using this document.

This is an audit: production checker code and existing tests were not changed.
The pre-existing `.gitignore` modification was left untouched. Graphify was
attempted as required by workspace instructions, but this repository has no
`graphify-out/graph.json`; the comparison therefore used the actual source.

## Executed verification

A temporary Python 3.12.15 environment was created outside the repository.

| Verification | Result |
| --- | --- |
| Install declared package and development dependencies, then run all tests | **59 passed, 2 failed**; both failures require undeclared `pydantic` |
| Add `pydantic` to the temporary environment and rerun all tests | **61 passed, 1 warning** |
| Reference submission exercising all five checker groups | **39 passed**, no failures/errors/skips |
| Combined broken submission exercising all five groups | **39 passed**, no failures/errors/skips |
| Individual broken-submission probes | **14 variants passed every check in their selected group** |
| Valid alternatives rejected by the checker | **3 confirmed**: Git ignore pattern, dotenv export syntax, spell-record output |
| Automatic detection of the PDF's complete file tree | Incorrectly selected **python_module_08** |
| Git ignore interpretation | Independently verified with `git check-ignore` |

Commands used for the repository tests:

```sh
/tmp/42tui-subject-audit-env/bin/python -m pip install -e '.[dev]'
/tmp/42tui-subject-audit-env/bin/python -m pytest -q
/tmp/42tui-subject-audit-env/bin/python -m pip install 'pydantic>=2,<3'
/tmp/42tui-subject-audit-env/bin/python -m pytest -q
```

Relevant installed versions: pytest 9.2.0, flake8 7.5.0, mypy 2.4.1,
python-dotenv 1.2.4, pydantic 2.14.3, and rich 15.0.0. Neither pandas nor numpy
was installed: this also demonstrates why the check named `Installed dependencies`
does not prove the installed-dependency scenario was tested.

The assert-based reproduction script and its 20 result records are available for
this session at `/tmp/42tui_subject_audit_probes.py` and
`/tmp/42tui-subject-audit-probes.json`. They use temporary student submissions and
the unchanged checker, with real flake8 and subprocess execution. The 20 records
comprise a reference run, 14 individually broken variants, three rejected valid
alternatives, a combined broken run, and a detection probe.

## Findings, ordered by impact

### F1 — Light validation accepts a validator that always rejects

**High.** PDF pp. 19–20; checker lines 393–404.

The assertions search for `"VALID"` as a substring. `"INVALID"` contains
`"VALID"`, so both positive and negative cases pass when both functions always
return `"INVALID"`. The required allowed-ingredient function can be absent,
and neither returned string needs to contain the ingredients or spell name.
Confirmed: **8/8 grimoire checks passed** with this implementation:

```python
def validate_ingredients(ingredients: str) -> str:
    return "INVALID"

def light_spell_record(spell_name: str, ingredients: str) -> str:
    return "INVALID"
```

Only `EARTH` and `unknown` are exercised. Missing cases include each of air,
fire, water, mixed case, multiple ingredients, and empty input. A validator
supporting earth alone also passed 8/8.

### F2 — The required transmutation function can be entirely absent

**High.** PDF pp. 16–18; checker lines 343–374.

`lead_to_gold()` is never imported or called. The recipe test only finds absolute
and relative import nodes anywhere in the AST. Both demonstration scripts can
be empty. Potion tests only search for element substrings, so they accept
incorrect sentences that never call the element functions. Confirmed:
**7/7 transmutation checks passed** with no recipe function, imports under
`if False:`, empty scripts, and incorrectly formatted potion results.

### F3 — Dependency management can be replaced by two printed words

**High.** PDF pp. 9–10; checker lines 81–115.

`loading.py` containing only `print("pip poetry")` passes. Requirements containing
only a comment and a pyproject containing invalid TOML both pass because only
nonempty text is required. The checker does not verify the declared packages,
matching constraints, imports, installed versions, meaningful install commands,
or the explanation of pip versus Poetry. It does not install either manifest or
ensure the supposed installed-dependency run has the student's packages.
Confirmed: **9/9 ex0 checks passed** with these broken files.

### F4 — The Oracle need not load dotenv or implement most configuration

**High.** PDF pp. 11–13; checker lines 142–239.

An import of `dotenv` satisfies `Use python-dotenv` without any call to load it.
The runtime test only requires two different stdout values when environment
variables change. Printing `os.getenv("MATRIX_MODE", "development")` is enough.
`DATABASE_URL`, `API_KEY`, `LOG_LEVEL`, and `ZION_ENDPOINT` can all be ignored;
the requirements file can be empty. No defaults or missing-configuration
warnings are checked. Dotenv precedence and API-key override are not established.
Confirmed: **8/8 ex1 checks passed** with dotenv never loaded and four keys unused.

### F5 — Demonstrations can be absent or unreachable

**High.** PDF pp. 15–21; checker lines 273–309, 343–344, 392–440;
shared helper lines 95–115.

`script()` checks only exit status. `expected_exception()` accepts any successful
exit or any stderr containing the exception name. AST checks count unreachable
imports and calls. Confirmed: an empty Alembic 0 script and Alembic 1 with its
hidden-earth call inside `if False:` passed **7/7**. Empty Kaboom 0 and Kaboom 1
with an unreachable dark import passed **8/8**. Creating air before trying earth,
actually recording spells, and the prescribed import forms in the other
demonstrations are not verified.

Keep accepting genuinely caught exceptions: the PDF explicitly permits catching
the Alembic and Kaboom exceptions. A fix must verify the behavior rather than
require a nonzero process exit.

### F6 — The dark pair need not contain a circular dependency

**High.** PDF pp. 19–21; checker lines 406–418.

A dark spellbook containing only `raise ImportError("circular import")` passes,
even if the dark validator is empty and every dark function is missing. The
checker matches error text without verifying two mutually dependent modules,
top-level imports, or dark ingredient definitions. Confirmed: **8/8** passed.

### F7 — Authorized imports are not enforced

**High.** PDF p. 5 and exercise headers; shared helper lines 156–214.

`policy()` has no authorized-import logic. Ex0 and ex1 can import unauthorized
modules; ex2–ex4 can import standard-library or third-party modules instead of
only project modules. Confirmed: `import json` in Alembic 0 passed **7/7**.
Existing import enforcement in the older Module 06 checker does not protect the
bis checker because it is a separate implementation.

### F8 — General annotation/type requirements are omitted

**High.** PDF p. 5, with an intentional-error exception on p. 15.

`BisTester.lint()` runs flake8 only. Neither mypy nor an annotation-presence
check runs. The README explicitly documents this limitation, but it still leaves
a subject requirement uncovered. Confirmed: unannotated element functions
passed **7/7**. The exemption for the intentional hidden-earth error does not
justify skipping all unrelated annotation and typing checks.

### F9 — Git ignore handling gives false passes and false failures

**High.** PDF pp. 12, 22; checker lines 134–140.

The checker searches for a literal `.env` or `/.env` line rather than the
effective Git rule. `.env\n!.env\n` passes even though Git does not ignore the
file. Conversely, `.[e]nv` correctly ignores `.env` in Git but is rejected.
Both were confirmed against Git itself. The checker also does not determine
whether `.env` was already tracked, which ignore rules cannot repair.

### F10 — Forbidden operations can be missed through ordinary aliases

**High.** PDF p. 5; shared helper lines 156–214.

Only direct `eval(...)`/`exec(...)` names and literal `sys.path` mutation forms
are recognized. Confirmed: `from builtins import eval as evaluate` and
`from sys import path`, followed by `evaluate(...)` and `path.append(...)`,
passed **7/7**. Helpers outside the explicit mandatory path lists are not scanned.
This policy is a limited static check, not a sandbox.

### F11 — Automatic detection chooses the wrong subject

**Medium.** PDF p. 6; `ModuleDetector.MODULE_SIGNATURES` in core.py.

There is a version label for `python_module_05_bis`, but no detection signature.
The PDF's full layout is detected as `python_module_08` because of
`ex0/construct.py`. The automatic CLI path therefore runs a checker with a
different folder layout, output expectations, and additional requirements.
The two existing detector regression tests cover only Module 09 versus 07.
For this PDF, explicitly select `germinette python_module_05_bis`.

### F12 — Correct spell-record output can be rejected

**Medium.** PDF p. 19; checker lines 401–402.

The validator must return the ingredients and a VALID/INVALID keyword. The
recorder's prose requirement is to state whether a spell was recorded or
rejected. The checker additionally requires VALID/INVALID inside the recorder's
return value, following the example more narrowly than the prose. A recorder
that consults the correct validator and returns `Spell recorded: test` or
`Spell rejected: test` is rejected. Confirmed: **1 failure among 8 grimoire checks**.

### F13 — Valid dotenv example syntax is rejected

**Medium.** PDF pp. 11–13; checker lines 150–158.

The homemade example parser treats `export MATRIX_MODE=development` as a key
named `export MATRIX_MODE`, so it reports all five exported keys missing.
python-dotenv 1.2.4 accepts optional `export` prefixes, as verified in the
[upstream file-format documentation](https://github.com/theskumar/python-dotenv/blob/v1.2.4/README.md#file-format)
through Context7 and by parsing the five exported assignments locally.
Confirmed: **1 failure among 8 ex1 checks** despite a valid example file.

### F14 — Environment information and submission exclusions are incomplete

**Medium.** PDF pp. 7–8, 22; checker lines 46–79 and exercise file lists.

A construct script printing only `venv activate` and `sys.prefix` passes 9/9;
it need not describe the current interpreter, environment name/status, or package
installation paths. Outside/inside runs do not reconcile inherited `VIRTUAL_ENV`
with the selected interpreter, which should be considered when improving the
environment test.

There is no submitted-file or tracked-file inspection for `.env` or virtual
environments. Adding a sample `.env` and a `lab_env/pyvenv.cfg` produced no
failure. This probe shows the absence of an exclusion check; it does not imply
that every untracked local `.env` should fail, since development requires one.
The relevant target is the submitted/tracked tree. Hardcoded real secrets also
receive no dedicated inspection; proving that a value is real requires review.

### F15 — Existing passing fixtures preserve these gaps

**Medium.** tests/test_bis_checkers.py lines 58–118.

The ex0 fixture intentionally imports no reagents, prints no installed versions,
and has no Poetry dependency declaration, yet is asserted to pass. The Alembic
fixture omits annotations and never demonstrates creating air through the
package before accessing earth. There are no Codex regression tests for
transmutation or grimoire, no complete Codex golden fixture, and no regression
that proves real `.env` loading and environment precedence succeed.

## Every recorded checker check

These are all **39** checks produced by the reference full run. Conditional
error/skip records are additional outcomes, not extra coverage of requirements.
`Covered` means the specific behavior named here is checked; it does not mean
the entire exercise is covered.

| Group / recorded name | PDF | What the implementation establishes | Assessment |
| --- | --- | --- | --- |
| ex0: Exercise 0 files | 7 | All four mandatory files exist | Covered |
| ex0: Exercise 0 flake8 | 5 | Runs flake8 on construct/loading | Covered for these files; helpers omitted |
| ex0: Exercise 0 forbidden operations | 5, 7 | Recognizes selected direct forbidden calls/mutations | Partial; F7, F10 |
| ex0: Environment detection | 7–8 | Both interpreters exit zero and stdout differs | Partial; F14 |
| ex0: Environment setup instructions | 7–8 | Outside stdout includes `venv` and `activat` | Partial; no usable commands required |
| ex0: Missing dependency guidance | 9 | Zero exit plus `pip` and `poetry` text | Partial; F3 |
| ex0: Loading dependencies | 9–10 | Runs with tester Python and requires zero exit | Partial; no installed libraries or versions guaranteed |
| ex0: Dependency declaration: requirements.txt | 9 | Nonempty text | Partial; F3 |
| ex0: Dependency declaration: pyproject.toml | 9 | Nonempty text | Partial; F3 |
| ex1: Exercise 1 files | 11 | All four mandatory files exist | Covered |
| ex1: Exercise 1 flake8 | 5 | Runs flake8 on oracle.py | Covered for this file; helpers omitted |
| ex1: Exercise 1 forbidden operations | 5, 11 | Selected direct calls/mutations | Partial; F7, F10 |
| ex1: Ignore .env | 12 | Finds literal line | Incorrect Git semantics; F9 |
| ex1: Example configuration | 12 | Finds five assignment-like key names | Partial; values not validated, valid syntax rejected; F13 |
| ex1: Use python-dotenv | 11 | Finds dotenv import | Partial; no usage proved; F4 |
| ex1: Oracle without configuration | 12–13 | Zero exit with five environment keys removed and local .env excluded | Partial; no defaults/warning assertion |
| ex1: Development and production | 12–13 | Zero exits and different stdout | Partial; dotenv and precedence not proved; F4 |
| alembic: Exercise 2 files | 14 | Five mandatory paths exist at root/package locations | Covered |
| alembic: Exercise 2 flake8 | 5 | Runs flake8 on the five listed files | Covered for listed files |
| alembic: Exercise 2 forbidden operations | 5, 14 | Selected direct calls/mutations | Partial; F7, F10 |
| alembic: ft_alembic_0.py | 15 | Zero exit | Partial; no import/call/output proof; F5 |
| alembic: Alembic package exports | 14–15 | Four exact element return strings, air exposed, earth absent from package | Covered for these six conditions |
| alembic: Alembic hidden access | 15 | AST contains import alchemy and matching create_earth call | Partial; dead code passes; air call absent; F5 |
| alembic: ft_alembic_1.py | 15 | Zero exit or AttributeError text in stderr | Partial; F5 |
| transmutation: Exercise 3 files | 16–18 | Five mandatory files/package markers exist | Covered |
| transmutation: Exercise 3 flake8 | 5 | Runs flake8 on the five listed files | Covered for listed files |
| transmutation: Exercise 3 forbidden operations | 5, 16 | Selected direct calls/mutations | Partial; F7, F10 |
| transmutation: ft_distillation_0.py | 16–17 | Zero exit | Partial; no demonstration or prescribed import verified; F5 |
| transmutation: ft_transmutation_0.py | 18 | Zero exit | Partial; no recipe invocation verified; F2 |
| transmutation: Potion behavior | 16–17 | Required element substrings appear in potion returns | Partial; exact return strings and use of functions missing; F2 |
| transmutation: Recipe import styles | 18 | Both styles appear anywhere in recipe AST | Partial; dead code counts; required function untested; F2 |
| grimoire: Exercise 4 files | 19–20 | Seven mandatory files/package markers exist | Covered |
| grimoire: Exercise 4 flake8 | 5 | Runs flake8 on the seven listed files | Covered for listed files |
| grimoire: Exercise 4 forbidden operations | 5, 19 | Selected direct calls/mutations | Partial; F7, F10 |
| grimoire: ft_kaboom_0.py | 20–21 | Zero exit | Partial; empty script passes; F5 |
| grimoire: Light grimoire | 19 | Four substring assertions for earth/unknown | Incorrect positive status test and overstrict recorder format; F1, F12 |
| grimoire: Dark circular import | 20–21 | ImportError text mentions circular/partially initialized | Partial; fabricated error passes; F6 |
| grimoire: Dark spellbook demonstration | 20 | Direct import appears somewhere in AST | Partial; unreachable import passes; F5 |
| grimoire: ft_kaboom_1.py | 20–21 | Zero exit or ImportError text in stderr | Partial; real demonstration not proved; F5 |

`Outside virtual environment`, `Inside virtual environment`, `Missing
dependencies`, `Installed dependencies`, `Oracle development`, and `Oracle
production` are subprocess operation labels; successful operations do not
themselves add extra records. Process failures create error records. Missing
flake8 or dotenv creates skip records. Malformed Python creates syntax failures.

## Remaining requirement coverage, including non-exercise chapters

This table accounts for requirements that cannot be inferred from the 39
recorded check names alone.

| PDF requirement | Pages | Status / required follow-up |
| --- | --- | --- |
| Python 3.10 or later | 5 | Tester package requires >=3.10; tested here on 3.12.15. Syntax/behavior on every supported Python is not established by one run. |
| Comprehensive annotations and mypy | 5 | Missing from bis checks; F8. Preserve the deliberate hidden-earth mypy exception on p. 15. |
| All builtins allowed except eval/exec | 5 | Policy should preserve permitted builtins while fixing alias misses; no additional builtin ban is justified. |
| Ex0 authorized os/sys/site/importlib/pandas/numpy | 7 | No whitelist enforcement; F7. |
| Ex1 authorized os/sys/dotenv/file operations | 11 | No whitelist enforcement; F7. |
| Ex2–ex4 only project imports | 5, 14, 16, 19 | No whitelist enforcement; F7. |
| No sys.path modification anywhere | 5 | Only some direct forms in listed files; F10. |
| Root layout; shared package grows across ex2–ex4 | 6 | All 25 required file paths are represented across the five file checks; no invented ex2/ex3/ex4 directories are required. |
| Distinguish global/virtual environment and package locations | 7–8 | Only stdout difference and instruction substrings checked; F14. |
| Fresh environment creation during review | 8, 22 | Manual demonstration; tester-created environment does not prove student understanding. |
| A couple of reagents in both manifests, matching constraints | 9–10 | Not checked beyond nonempty text; F3. Do not add matplotlib/requests requirements from the older Matrix subject. |
| Every declared reagent imported, version reported | 9–10 | Missing; F3. |
| Helpful missing-reagent commands for pip and Poetry | 9 | Only manager names checked; F3. |
| Explain pip resolution versus Poetry lockfile | 9–10 | Not established; F3. `poetry.lock` is discussed, but not listed as a mandatory submission file. |
| Actual dotenv load and handling all five variables | 11–13 | Missing semantic verification; F4. |
| Environment takes priority over dotenv | 13 | Output difference does not prove precedence; F4. |
| Defaults and warnings without config | 13 | Only no-crash behavior is checked. |
| No real secrets committed; no submitted .env/venv | 12, 22 | No submitted-tree/Git tracking checks; F9, F14. Secret authenticity needs human review. |
| Root fire/water and package earth/air exact strings | 14 | Covered by package probe. |
| Air exposed, earth unavailable through package interface | 14–15 | Covered by package probe. `__all__` is not mandated if another standard export convention works. |
| Alembic 0 imports root module and creates fire | 15 | Script semantics missing; F5. |
| Alembic 1 imports alchemy, creates air, then tries hidden earth | 15 | Partial AST test; executed order and air call missing; F5. |
| Healing/strength use element functions and specified sentences | 16–17 | Element substrings only; F2. |
| Distillation uses from-import and brews both potions | 16–17 | Not verified; F5. |
| Recipe returns specified composed lead-to-gold string | 18 | No function check at all; F2. |
| Recipe uses absolute and relative imports | 18 | Static presence only; F2. |
| Transmutation script imports recipe module and invokes recipe | 18 | Not verified; F2. |
| Light allowed ingredients exactly earth/air/fire/water | 19 | Required function never called; F1. |
| Validator includes ingredients and correct status, case insensitive | 19 | Incomplete inputs and invalid substring check; F1. |
| Spell recorder delegates to validator, records or rejects correctly | 19 | Delegation/decision/output not verified; F1, F12. |
| Light pair has mutual dependency but survives | 19–20 | Direct imports succeed, but dependency relationship not checked. |
| Dark functions/ingredients bats/frogs/arsenic/eyeball | 20 | Not checked; F6. |
| Dark pair fails because of naive mutual top-level imports | 20 | Error text only; F6. |
| Kaboom scripts access specified package/module and record spells | 20–21 | Partial static imports and exit statuses; F5. |
| Exceptions may be caught or uncaught | 15, 20 | Current helper allows both, but also allows no exception at all; F5. |
| Understand imports, exports, environments and cycle repair | 2–4, 10, 13, 15, 18, 21–22 | Human/peer evaluation; cannot be certified by automated output checks. |
| Use and understand AI-generated work, seek peer review | 3–4 | Learning/evaluation guidance; no automated conformance claim appropriate. |

The general instruction that functions return strings has an explicit exercise
exception: the ingredient-list function on p. 19 returns a list. A checker should
follow that more specific requirement. The p. 20 prose requests dark-prefixed
counterparts, while the p. 21 traceback imports `validate_ingredients` without a
dark prefix. Preserve this documented ambiguity rather than imposing an
unsupported single interpretation when strengthening the dark tests.

## Every regression test and its applicability

There are **61 test functions in 18 test files**. Seven directly exercise Codex
or its shared report/policy behavior. Five more in the same file target the
different Nexus bis subject. The other 49 target older/different subjects or
shared infrastructure. Similar names do not make an older subject's tests a
valid conformance suite for this PDF.

All seven directly relevant tests are in
[test_bis_checkers.py](tests/test_bis_checkers.py):

| Test function | Comparison with this PDF |
| --- | --- |
| test_missing_files_fail_for_both_subjects | Correctly checks five exercise file failures in an empty directory. No content coverage. |
| test_cli_report_contains_failed_results | Correctly checks JSON/exit status for missing files. No successful end-to-end Codex coverage. |
| test_codex_environment_checks_inside_outside_and_missing_packages | Tests interpreter contrast but asserts a noncompliant loader/manifests pass; F3, F14, F15. |
| test_codex_alembic_accepts_expected_exception | Covers exports, uncaught expected exception, wrong exception, and absent hidden-call syntax. Passing fixture omits required air demonstration and annotations; F5, F8, F15. |
| test_report_skipped_counts_and_incomplete_run | Correctly checks skipped dotenv accounting and runner returning None. Does not test successful dotenv loading. |
| test_unknown_exercise_produces_reported_failure | Correctly checks invalid filter accounting; infrastructure requirement. |
| test_policy_distinguishes_reading_and_mutating_sys_path | Correct for direct read/append forms. No alias or deletion coverage; F10. |

The other five tests in that file are
`test_nexus_processor_checks_structure_and_execution`,
`test_nexus_processor_passing_and_invalid_ingestion`,
`test_factory_contract_requires_two_implementations`,
`test_factory_runtime_checks_transform_and_package_exports`, and
`test_strategy_runtime_checks_order_and_invalid_entity`. They target
`python_module_06_bis` and are not requirements of this PDF.

| Other test file | Test functions | Applicability |
| --- | ---: | --- |
| test_module00_v30_alignment.py | 2 | Different Module 00 v3.0 subject |
| test_module01_v30_alignment.py | 4 | Different Module 01 v3.0 subject |
| test_module02_v30_alignment.py | 2 | Different Module 02 v3.0 subject |
| test_module03_v30_alignment.py | 5 | Different Module 03 v3.0 subject |
| test_module04_v30_alignment.py | 3 | Different Module 04 v3.0 subject |
| test_module05_v30_alignment.py | 2 | Different Module 05 v3.0 subject; not Codex bis |
| test_module06_v20_alignment.py | 4 | Older Codex v2.0; expects extra Alembic scripts, including hidden-earth demonstration in ft_alembic_4.py rather than this PDF's ft_alembic_1.py |
| test_module07_v30_alignment.py | 2 | Different DataDeck v3.0 subject |
| test_integration_module07.py | 2 | Golden fixture for Module 07 only; no Codex golden fixture |
| test_module08_v30_alignment.py | 3 | Older Matrix v3.0; separates construct/loading/oracle across ex0/ex1/ex2 and includes unrelated visualization dependencies |
| test_module09_v30_alignment.py | 4 | Different Pydantic subject; two tests fail without undeclared pydantic |
| test_module10_v30_alignment.py | 3 | Different Module 10 v3.0 subject |
| test_a_maze_ing_checker_alignment.py | 4 | Different maze subject |
| test_a_maze_ing_checker_seed_logic.py | 3 | Different maze subject |
| test_module_detector_alignment.py | 2 | Shared detection, but only Module 09 versus 07; misses Codex bis misclassification |
| test_legacy_reports.py | 3 | Legacy accounting/reporting, not BisTester conformance |
| test_mypy_fallback.py | 1 | Legacy BaseTester mypy crash fallback; bis lint does not invoke it |

The repository CI installs only `.[dev]` and then runs the complete suite.
`pyproject.toml` declares pytest in that extra but not pydantic. This matches the
clean-install failures reproduced here. Adding pydantic to this audit's temporary
environment made all 61 pass; it did not change or repair Codex coverage.

## Smallest complete remediation scope

1. Fix F1/F12 together: exact positive/negative validator status, required allowed
   list, varied light inputs, and recorder decisions without imposing example-only
   wording. Add focused regression cases for always-INVALID and valid recorder prose.
2. Exercise `lead_to_gold()` and exact potion/recipe compositions. Verify the
   required scripts actually execute their demonstrated operations, and test both
   caught and uncaught expected failures. Cover ex3/ex4 with a Codex reference tree.
3. Parse and compare real dependency declarations; test absent and present packages
   in controlled environments and require actual versions and useful guidance.
   Test real dotenv loading and environment precedence for the five specified keys.
4. Apply authorized-import and forbidden-operation checks across submitted project
   Python files, with ordinary import aliases handled. Check annotations/types
   without failing the explicitly intentional hidden-export error.
5. Verify Git ignore semantics and submitted/tracked exclusions, fix Codex bis
   detection, and make existing passing fixtures conform to this PDF.
6. Declare the test dependency needed by the full repository suite. Preserve the
   older modules as separate subjects; do not rename their versions or merge their
   extra requirements into this PDF's checker.

Affected implementation locations: `python_module_05_bis.py`, `bis_common.py`,
and Codex bis detection in `core.py`. A change to shared helpers must also check
their Nexus bis callers. Affected verification: `test_bis_checkers.py`,
`test_module_detector_alignment.py`, a Codex fixture, package development
dependencies, CI, and the README's coverage description. Existing CLI/report
consumers should retain the version-1 count/check schema and correct skip/error
exit behavior.

No automatic checker can establish the required peer-review understanding.
The tested passing reports currently leave substantial functional requirements
unverified; use them as limited diagnostics until the gaps above are repaired.

## Remediation on feat/legacy-json-report

The user authorized fixing the findings against the attached **v1.0** PDF.
The checker has been reworked on this branch; no version 3.1 claim or relabeling
was introduced. The original evidence above remains a record of the earlier
revision, not the current checker.

| Findings | Implemented correction | Regression evidence |
| --- | --- | --- |
| F1, F12 | Match VALID/INVALID as complete tokens; exercise all light ingredients, mixed case and invalid/empty inputs; check allowed-list/validator/recorder dependencies and accept recorded/rejected prose without mandatory status suffixes | Always-INVALID and earth-only validators fail; valid recorder prose and package from-import pass |
| F2 | Call potions and lead_to_gold, compare composed return values, change element results to prove functions are used, and require both recipe import styles to execute | Missing recipe, malformed potion results and dead imports fail |
| F3 | Parse TOML and requirements, compare version ranges, verify actual reagent imports/versions, test no reagents and individually missing reagents, and check manager guidance/comparison | Empty/comment-only/mismatched/invalid manifests and dummy loading fail; equivalent pip/Poetry constraints and find_spec-based loading pass |
| F4 | Observe real dotenv calls and configuration reads/dictionaries, supply all five values through dotenv and conflicting environment values, check defaults/warnings and visible mode changes | Imported-but-unused dotenv, ignored keys, empty dependency declaration and override=True fail; dotenv dictionary composition passes |
| F5 | Observe executed import lines, required calls, printed results and genuine exception events; enforce air before hidden earth and require a dark spell-record attempt | Empty/unreachable demonstrations and reversed Alembic order fail; caught and uncaught teaching exceptions pass |
| F6 | Require the dark function definitions and mutual top-level imports; verify both imports executed and both files participated in the actual cycle; inspect dark behavior separately in a subprocess with only the mutual imports deferred | Fabricated errors, errors before mutual import, unreachable imports and incorrect dark ingredients fail; both PDF validator naming variants pass |
| F7, F10 | Apply exercise import policies across exercise files/helpers; resolve ordinary import/assignment aliases; detect direct/aliased eval, exec and sys.path mutations, including deletion | Unauthorized helper imports and forbidden aliases/deletions fail; path reads and alias creation pass |
| F8 | Run mypy with annotated definitions required, independent of student config; exempt only the intentional alchemy.create_earth attribute diagnostic in ft_alembic_1.py | Untyped helper fails; the complete annotated fixture and intended hidden-export error pass |
| F9, F13 | Use Git's effective ignore semantics and python-dotenv's parser | Negated ignore fails; effective glob and export-prefixed assignments pass |
| F11 | Detect using ex0/loading.py and ex1/oracle.py, which distinguish this PDF from older subjects | Full Codex tree detects as 05 bis; legacy Codex and Matrix detection remain correct |
| F14 | Verify executable/environment/package-location output, clean inherited activation, resolve the real base interpreter, use platform venv defaults and inspect tracked .env/venv files | Minimal prefix-only output fails; poisoned activation passes; tracked secrets/venvs fail while unsubmitted local files are allowed; Python 3.10 standalone venv behavior is exercised |
| F15 | Replace the passing incomplete Codex fixtures with a complete reference tree and add positive, negative, combined-failure and CLI report regressions | All five groups are checked in one successful reference run and in one broken run that must fail each group |

The JSON version-1 result schema and the success/failure/incomplete exit codes are
preserved. Shared helper changes are covered by the existing Nexus bis tests.
Pydantic, pandas and numpy are declared in the development extra so the complete
suite is reproducible. Runtime declaration parsing adds `packaging>=26.3`, whose
[version-range comparisons](https://packaging.pypa.io/en/stable/specifiers.html#packaging.specifiers.SpecifierSet.to_range)
avoid rejecting equivalent constraint syntax, plus the conditional TOML backport
for Python 3.10. No student package installations or source edits are performed.

Remaining manual boundaries are explicit in the README: Poetry installation
itself is not executed; unavailable/mismatched installed reagents, direct URL
dependency sources and non-Git submission inspection are reported as skips.
Human review still establishes whether a committed value is a real secret and
whether the student understands the required concepts. Static policy checks are
not a sandbox for hostile code or dynamically constructed names.

Final verification on macOS:

| Check | Result |
| --- | --- |
| Full suite, fresh Python 3.10.22 environment installed with `.[dev]` | **116 passed**, one existing Pydantic deprecation warning |
| Full suite, Python 3.12.15 environment | **116 passed**, the same warning |
| flake8 on the changed checker/helper/tests and Codex reference files | Passed |
| `git diff --check` | Passed |
| `pip check` in both environments | No broken requirements |
| Build wheel and inspect archive/metadata | Runtime helper and required dependency declarations included |

Linux and Windows were not executed locally. The existing CI matrix covers
Python 3.10/3.12 on Ubuntu. The existing user modification to `.gitignore` is
preserved; source changes, tests and documentation remain uncommitted on this
branch. A local structural code graph was generated/refreshed under `graphify-out/`
as required by workspace instructions.
