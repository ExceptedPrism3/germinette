"""Code Nexus: Abstract Architecture v1.0."""

import ast
from pathlib import Path

from germinette.subjects.bis_common import BisTester
from germinette.subjects.combat_checks import (
    FACTORIES,
    STRATEGIES,
    DEMONSTRATION,
)
from germinette.subjects.nexus_checks import (
    PROCESSORS,
    STREAM,
    PIPELINE,
    intentional_ingest_errors,
)


class Tester(BisTester):
    def __init__(self):
        super().__init__()
        self.title = (
            "[bold cyan]Testing Module 06 bis: Code Nexus (v1.0)[/bold cyan]"
        )
        self.exercises = [
            ("data_processor", self.processor),
            ("data_stream", self.stream),
            ("data_pipeline", self.pipeline),
            ("ex3", self.factories),
            ("ex4", self.strategies),
        ]

    def lint(self, name, paths):
        errors = []
        for path in paths:
            tree = self.tree(path)
            if tree is None:
                continue
            expected = (
                intentional_ingest_errors(tree)
                if str(path) == "data_processor.py"
                else []
            )
            style = self.check_flake8(str(path), expected_mypy_errors=expected)
            hints = self.check_type_hints(path)
            errors.extend(error for error in (style, hints) if error)
        self.check(name + " and types", not errors, "\n".join(errors))

    def classes(self, path, required):
        tree = self.tree(path)
        if tree is None:
            return
        classes = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        }
        for name, methods in required.items():
            node = classes.get(name)
            found = (
                {
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                if node
                else set()
            )
            self.check(
                f"{path}: {name}",
                node is not None and set(methods) <= found,
                f'{name} must define: {", ".join(methods)}',
            )

    def processor(self):
        path = "data_processor.py"
        if self.files("Exercise 0 files", [path]):
            self.lint(f"{path}: flake8", [path])
            self.policy(
                f"{path}: forbidden operations",
                [path],
                allowed_imports={"abc", "typing", "__future__"},
            )
            self.classes(
                path,
                {
                    "DataProcessor": ["validate", "ingest", "output"],
                    "NumericProcessor": ["validate", "ingest"],
                    "TextProcessor": ["validate", "ingest"],
                    "LogProcessor": ["validate", "ingest"],
                },
            )
            self.script(path)
            self.probe(
                "Processor validation and FIFO",
                (
                    "from data_processor import (DataProcessor, "
                    "NumericProcessor, "
                    "TextProcessor, LogProcessor)\n"
                )
                + PROCESSORS,
            )

    def stream(self):
        path = "data_stream.py"
        if self.files("Exercise 1 files", [path]):
            self.lint(f"{path}: flake8", [path])
            self.policy(
                f"{path}: forbidden operations",
                [path],
                allowed_imports={"abc", "typing", "__future__"},
            )
            self.classes(
                path,
                {
                    "DataStream": [
                        "register_processor",
                        "process_stream",
                        "print_processors_stats",
                    ]
                },
            )
            self.script(path)
            self.probe(
                "Stream routing",
                (
                    "from data_stream import (DataProcessor, DataStream, "
                    "NumericProcessor, TextProcessor, LogProcessor)\n"
                )
                + STREAM,
            )

    def pipeline(self):
        path = "data_pipeline.py"
        if self.files("Exercise 2 files", [path]):
            self.lint(f"{path}: flake8", [path])
            self.policy(
                f"{path}: forbidden operations",
                [path],
                allowed_imports={"abc", "typing", "__future__"},
            )
            self.classes(
                path,
                {
                    "ExportPlugin": ["process_output"],
                    "DataStream": ["output_pipeline"],
                },
            )
            self.script(path)
            self.probe(
                "Pipeline plugin dispatch",
                (
                    "import data_pipeline\n"
                    "globals().update(vars(data_pipeline))\n"
                )
                + PIPELINE,
            )

    def factories(self):
        if self.files(
            "Exercise 3 files",
            ["ex3/__init__.py", "battle.py", "capacitor.py"],
        ):
            self.lint(
                "Exercise 3 flake8",
                ["battle.py", "capacitor.py", *Path("ex3").rglob("*.py")],
            )
            self.policy(
                "Exercise 3 forbidden operations",
                ["battle.py", "capacitor.py", *Path("ex3").rglob("*.py")],
                allowed_imports={"abc", "typing"},
            )
            self.script("battle.py")
            self.script("capacitor.py")
            self.probe(
                "Factory demonstration",
                "SCRIPT = 'battle.py'\nREQUIRED = {'create_base': 4, "
                "'create_evolved': 2, 'describe': 6, 'attack': 6}\n"
                + DEMONSTRATION,
            )
            self.probe(
                "Capability demonstration",
                "SCRIPT = 'capacitor.py'\nREQUIRED = {'create_base': 1, "
                "'create_evolved': 1, 'describe': 2, 'attack': 4, "
                "'transform': 2, 'revert': 2}\n" + DEMONSTRATION,
            )
            self.probe(
                "Factory and capability behavior",
                (
                    "PACKAGES = ['ex3']; PACKAGE = 'ex3'\n"
                    "CAPABILITIES = True; HEALING = False\n"
                )
                + FACTORIES,
                can_skip=True,
            )
            self.package_contract(
                "ex3",
                [
                    ("Creature interface", {"attack", "describe"}),
                    ("Transform capability", {"transform", "revert"}),
                    ("Factory interface", {"create_base", "create_evolved"}),
                ],
            )

    def strategies(self):
        if self.files(
            "Exercise 4 files", ["ex4/__init__.py", "tournament.py"]
        ):
            self.lint(
                "Exercise 4 flake8",
                ["tournament.py", *Path("ex4").rglob("*.py")],
            )
            self.policy(
                "Exercise 4 forbidden operations",
                ["tournament.py", *Path("ex4").rglob("*.py")],
                allowed_imports={"abc", "typing"},
            )
            self.script("tournament.py")
            self.probe(
                "Strategy demonstration",
                "SCRIPT = 'tournament.py'\n"
                "REQUIRED = {'create_base': 2, 'act': 2, 'attack': 1}\n"
                + DEMONSTRATION,
            )
            self.probe(
                "Strategy behavior",
                (
                    "PACKAGES = ['ex3', 'ex4']; STRATEGY_PACKAGE = 'ex4'\n"
                    "HEALING = False\n"
                )
                + STRATEGIES,
                can_skip=True,
            )
            self.package_contract(
                "ex4", [("Strategy interface", {"act", "is_valid"})]
            )
            trees = [self.tree(path) for path in Path("ex4").rglob("*.py")]
            trees = [tree for tree in trees if tree]
            self.check(
                "Capability-based strategy",
                any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "isinstance"
                    for tree in trees
                    for node in ast.walk(tree)
                ),
                "The subject requires strategies to check capabilities "
                "using isinstance.",
            )

    def package_contract(self, directory, contracts):
        classes = []
        for path in Path(directory).rglob("*.py"):
            tree = self.tree(path)
            if tree:
                classes.extend(
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                )
        for label, required in contracts:
            abstract = required - {"describe"}
            candidates = []
            for cls in classes:
                methods = {
                    node.name: node
                    for node in cls.body
                    if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef)
                    )
                }
                if not required <= methods.keys():
                    continue

                def decorated(method):
                    return any(
                        (isinstance(d, ast.Name) and d.id == "abstractmethod")
                        or (
                            isinstance(d, ast.Attribute)
                            and d.attr == "abstractmethod"
                        )
                        for d in method.decorator_list
                    )

                bases = {
                    b.id if isinstance(b, ast.Name) else b.attr
                    for b in cls.bases
                    if isinstance(b, (ast.Name, ast.Attribute))
                }
                if "ABC" in bases and all(
                    decorated(methods[name]) for name in abstract
                ):
                    candidates.append(cls)
            self.check(
                label,
                bool(candidates),
                "Expected an ABC with abstract methods: "
                + ", ".join(sorted(abstract)),
            )
            if candidates and label in {
                "Factory interface",
                "Strategy interface",
            }:
                names = {candidate.name for candidate in candidates}
                concrete = [
                    cls
                    for cls in classes
                    if any(
                        (isinstance(base, ast.Name) and base.id in names)
                        or (
                            isinstance(base, ast.Attribute)
                            and base.attr in names
                        )
                        for base in cls.bases
                    )
                ]
                self.check(
                    label + " implementations",
                    len(concrete) >= 2,
                    "Expected at least two implementations of the "
                    "abstract interface.",
                )
