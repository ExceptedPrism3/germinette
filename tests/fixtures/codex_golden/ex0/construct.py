import site
import sys

print("Current Python:", sys.executable)
print("Environment Path:", sys.prefix)
print("Reagent installation paths:", site.getsitepackages())
if sys.prefix == sys.base_prefix:
    print("Open: python3 -m venv lab_env; source lab_env/bin/activate")
else:
    print("Sealed:", sys.prefix)
