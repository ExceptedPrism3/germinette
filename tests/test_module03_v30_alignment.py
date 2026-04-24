"""Regression tests for Module 03 v3.0 checker alignment."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def _assert_ok(tester, label: str) -> None:
    errors = tester.grouped_errors.get(label, [])
    assert not errors, f"{label} should pass but failed with:\n{errors}"


def test_module03_ex2_allows_round_and_math_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from germinette.subjects.python_module_03 import Tester

    _write(
        tmp_path / "ex2" / "ft_coordinate_system.py",
        """
        import math


        def get_player_pos() -> tuple[float, float, float]:
            while True:
                raw: str = input(
                    "Enter new coordinates as floats in format 'x,y,z': "
                )
                parts: list[str] = [p.strip() for p in raw.split(",")]
                try:
                    x_raw, y_raw, z_raw = parts
                except ValueError:
                    print("Invalid syntax")
                    continue
                try:
                    x = float(x_raw)
                    y = float(y_raw)
                    z = float(z_raw)
                    return (x, y, z)
                except ValueError as e:
                    print(f"Error on parameter'{raw}': {e}")


        def main() -> None:
            print("=== Game Coordinate System ===")
            print("Get a first set of coordinates")
            pos1 = get_player_pos()
            center = math.sqrt(pos1[0] ** 2 + pos1[1] ** 2 + pos1[2] ** 2)
            print(f"Distance to center: {round(center, 4)}")
            print("Get a second set of coordinates")
            pos2 = get_player_pos()
            dist = math.sqrt(
                (pos2[0] - pos1[0]) ** 2
                + (pos2[1] - pos1[1]) ** 2
                + (pos2[2] - pos1[2]) ** 2
            )
            print(f"Distance between the 2 sets of coordinates: {round(dist, 4)}")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_coordinate_system()
    _assert_ok(tester, "Exercise 2")


def test_module03_ex4_accepts_inventory_system_analysis_header(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_03 import Tester

    _write(
        tmp_path / "ex4" / "ft_inventory_system.py",
        """
        import sys


        def main() -> None:
            print("=== Inventory System Analysis ===")
            inventory: dict[str, int] = {}
            order: list[str] = []
            for arg in sys.argv[1:]:
                if ":" not in arg:
                    print(f"Error - invalid parameter'{arg}'")
                    continue
                name, qty_raw = arg.split(":", 1)
                if name in inventory:
                    print(f"Redundant item '{name}' - discarding")
                    continue
                try:
                    qty = int(qty_raw)
                except ValueError as e:
                    print(f"Quantity error for'{name}': {e}")
                    continue
                inventory[name] = qty
                order.append(name)

            total = sum(inventory.values()) if len(inventory) else 0
            print(f"Got inventory: {inventory}")
            print(f"Item list: {list(inventory.keys())}")
            print(f"Total quantity of the {len(inventory)} items: {total}")
            for name in order:
                pct = round((inventory[name] / total) * 100, 1) if total else 0.0
                print(f"Item {name} represents {pct}%")

            if len(order):
                max_name = order[0]
                min_name = order[0]
                for name in order:
                    if inventory[name] > inventory[max_name]:
                        max_name = name
                    if inventory[name] < inventory[min_name]:
                        min_name = name
                max_qty = inventory[max_name]
                min_qty = inventory[min_name]
                print(
                    f"Item most abundant: {max_name} "
                    f"with quantity {max_qty}"
                )
                print(
                    f"Item least abundant: {min_name} "
                    f"with quantity {min_qty}"
                )

            inventory.update({"magic_item": 1})
            print(f"Updated inventory: {inventory}")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_inventory_system()
    _assert_ok(tester, "Exercise 4")


def test_module03_ex5_accepts_player_action_stream_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_03 import Tester

    _write(
        tmp_path / "ex5" / "ft_data_stream.py",
        """
        import random
        from typing import Generator


        def gen_event() -> Generator[tuple[str, str], None, None]:
            players = ["alice", "bob", "charlie", "dylan"]
            actions = [
                "run",
                "eat",
                "sleep",
                "grab",
                "move",
                "climb",
                "swim",
                "release",
                "use",
            ]
            while True:
                yield (random.choice(players), random.choice(actions))


        def consume_event(
            events: list[tuple[str, str]]
        ) -> Generator[tuple[str, str], None, None]:
            while len(events):
                idx = random.randrange(len(events))
                event = events.pop(idx)
                yield event


        def main() -> None:
            print("=== Game Data Stream Processor ===")
            stream = gen_event()
            for i in range(1000):
                name, action = next(stream)
                print(f"Event {i}: Player {name} did action {action}")

            events = [next(stream) for _ in range(10)]
            print(f"Built list of 10 events: {events}")
            for e in consume_event(events):
                print(f"Got event from list: {e}")
                print(f"Remains in list: {events}")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_data_stream()
    _assert_ok(tester, "Exercise 5")


def test_module03_ex6_allows_random_and_requires_list_dict_comprehensions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_03 import Tester

    _write(
        tmp_path / "ex6" / "ft_data_alchemist.py",
        """
        import random


        def main() -> None:
            print("=== Game Data Alchemist ===")
            players = [
                "Alice",
                "bob",
                "Charlie",
                "dylan",
                "Emma",
                "Gregory",
                "john",
                "kevin",
                "Liam",
            ]
            cap_all = [p.capitalize() for p in players]
            cap_only = [p for p in players if p[:1].isupper()]
            scores = {name: random.randint(50, 999) for name in cap_all}
            average = round(sum(scores.values()) / len(scores), 2)
            high_scores = {k: v for k, v in scores.items() if v > average}
            print(f"Initial list of players: {players}")
            print(f"New list with all names capitalized: {cap_all}")
            print(f"New list of capitalized names only: {cap_only}")
            print(f"Score dict: {scores}")
            print(f"Score average is {average}")
            print(f"High scores: {high_scores}")


        if __name__ == "__main__":
            main()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_data_alchemist()
    _assert_ok(tester, "Exercise 6")
