# Codex reference submission

This tree follows the attached **The Codex v1.0** PDF (Module 05 bis). The tests
copy it into a temporary Git repository before running the checker. Install the
tester's development extra to provide pandas, numpy, mypy, flake8 and dotenv.

`ft_alembic_1.py` intentionally raises AttributeError. The dark spellbook pair
intentionally has a circular import, so `ft_kaboom_1.py` raises ImportError.
Those examples may also catch their respective errors. The light spellbook
uses a deferred import to preserve its working mutual dependency.

No real secrets, .env file, virtual environment, or Poetry lockfile is included.
