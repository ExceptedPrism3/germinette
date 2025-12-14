from setuptools import setup, find_packages

setup(
    name="germinette",
    version="1.0.0",
    description="Testing tool for 42 Python projects",
    author="ExceptedPrism3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "germinette=germinette.__main__:main",
            "pypaco=germinette.__main__:main",  # Alias just in case
        ],
    },
    install_requires=[
        "rich",  # For pretty output
    ],
    python_requires=">=3.10",
)
