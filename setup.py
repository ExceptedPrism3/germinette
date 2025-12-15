from setuptools import setup, find_packages

import re

# Read version from __init__.py
with open("germinette/__init__.py", "r", encoding="utf-8") as f:
    version = re.search(r'__version__\s*=\s*"(.*?)"', f.read()).group(1)

setup(
    name="germinette",
    version=version,
    description="Testing tool for 42 Python projects",
    author="ExceptedPrism3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "germinette=germinette.__main__:main",
        ],
    },
    install_requires=[
        "rich",  # For pretty output
    ],
    python_requires=">=3.10",
)
