import importlib

for name in ("pandas", "numpy"):
    try:
        reagent = importlib.import_module(name)
        print(name, reagent.__version__)
    except ImportError:
        print(name, "missing: pip install -r ex0/requirements.txt")
        print("poetry install")
print("pip resolves requirements.txt at installation time.")
print("Poetry resolves pyproject.toml and locks versions in poetry.lock.")
