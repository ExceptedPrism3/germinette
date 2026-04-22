import os
import re
import ast
import subprocess
import tempfile
from pathlib import Path
from collections import deque
from rich.console import Console
from rich.panel import Panel

from germinette.core import BaseTester

console = Console()


class Tester(BaseTester):
    def __init__(self):
        self.grouped_errors = {}
        self.warnings = []

    def record_error(self, exercise_label, error_type, message):
        if exercise_label not in self.grouped_errors:
            self.grouped_errors[exercise_label] = []
        self.grouped_errors[exercise_label].append(
            f"[bold]{error_type}[/bold]\n{message}"
        )

    def _error_count(self, exercise_label):
        return len(self.grouped_errors.get(exercise_label, []))

    def run(self, exercise_name=None):
        console.print("[bold purple]Testing Project: A-Maze-ing (v2.1)[/bold purple]")
        self.test_structure_and_files()
        self.test_makefile()
        self.test_config_format()
        self.test_readme_requirements()
        self.test_reusable_module()
        self.test_main_script_and_output()
        self.test_seed_interactive_regen_logic()

        if self.grouped_errors:
            console.print()
            console.rule("[bold red]Detailed Error Report[/bold red]")
            console.print()
            for label, messages in self.grouped_errors.items():
                content = "\n\n[dim]────────────────────────────────[/dim]\n\n".join(messages)
                console.print(
                    Panel(
                        content,
                        title=f"[bold red]{label}[/bold red]",
                        border_style="red",
                        expand=False,
                    )
                )
                console.print()

        if self.warnings:
            console.rule("[bold yellow]Non-blocking Warnings[/bold yellow]")
            console.print(
                "[yellow]These warnings do not fail the checker, but are useful for final submission readiness.[/yellow]"
            )
            for w in self.warnings:
                console.print(f"[yellow]- {w}[/yellow]")

    def test_structure_and_files(self):
        label = "Structure"
        console.print("\n[bold]Checking mandatory files[/bold]")
        cwd = Path(os.getcwd())
        required = ["a_maze_ing.py", "Makefile", "README.md", "config.txt"]
        missing = []
        for name in required:
            if (cwd / name).exists():
                console.print(f"[green]OK ({name} found)[/green]")
            else:
                console.print(f"[red]KO ({name} missing)[/red]")
                missing.append(name)

        if missing:
            self.record_error(
                label,
                "Missing Files",
                "Missing required project files:\n- " + "\n- ".join(missing),
            )

    def test_makefile(self):
        label = "Makefile"
        console.print("\n[bold]Checking Makefile targets[/bold]")
        before = self._error_count(label)
        path = Path("Makefile")
        if not path.exists():
            return
        txt = path.read_text(encoding="utf-8", errors="replace")
        required_targets = ["install:", "run:", "debug:", "clean:", "lint:"]
        missing = [t[:-1] for t in required_targets if t not in txt]
        if missing:
            console.print("[red]KO (Missing targets)[/red]")
            self.record_error(
                label,
                "Missing Targets",
                "Makefile is missing required targets:\n- " + "\n- ".join(missing),
            )
            return
        if "mypy" not in txt or "flake8" not in txt:
            self.record_error(
                label,
                "Lint Rule",
                "Makefile lint target should include both flake8 and mypy.",
            )
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")

    def test_config_format(self):
        label = "Config File"
        console.print("\n[bold]Checking config.txt format[/bold]")
        before = self._error_count(label)
        path = Path("config.txt")
        if not path.exists():
            return
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        cfg = {}
        for i, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                self.record_error(
                    label, "Format Error", f"Line {i} is not KEY=VALUE: {raw}"
                )
                return
            k, v = line.split("=", 1)
            cfg[k.strip().upper()] = v.strip()

        mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
        missing = [k for k in mandatory if k not in cfg]
        if missing:
            self.record_error(
                label,
                "Missing Keys",
                "Missing mandatory config keys:\n- " + "\n- ".join(missing),
            )
            return

        try:
            w = int(cfg["WIDTH"])
            h = int(cfg["HEIGHT"])
            ex, ey = [int(x) for x in cfg["ENTRY"].split(",")]
            ox, oy = [int(x) for x in cfg["EXIT"].split(",")]
        except Exception as e:
            self.record_error(label, "Type Error", f"Invalid numeric config values: {e}")
            return

        if w <= 0 or h <= 0:
            self.record_error(label, "Value Error", "WIDTH and HEIGHT must be > 0.")
        if not (0 <= ex < w and 0 <= ey < h):
            self.record_error(label, "Bounds Error", "ENTRY is outside maze bounds.")
        if not (0 <= ox < w and 0 <= oy < h):
            self.record_error(label, "Bounds Error", "EXIT is outside maze bounds.")
        if (ex, ey) == (ox, oy):
            self.record_error(label, "Value Error", "ENTRY and EXIT must be different.")
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")

    def test_readme_requirements(self):
        label = "README"
        console.print("\n[bold]Checking README requirements[/bold]")
        before = self._error_count(label)
        path = Path("README.md")
        if not path.exists():
            return
        txt = path.read_text(encoding="utf-8", errors="replace")
        first_line = txt.splitlines()[0].strip() if txt.splitlines() else ""
        first_line_re = re.compile(
            r"^\*This project has been created as part of the 42 curriculum by .+\*\s*$"
        )
        if not first_line_re.match(first_line):
            self.record_error(
                label,
                "First Line",
                "First README line must be italicized and match the required sentence format.",
            )

        required_sections = ["Description", "Instructions", "Resources"]
        missing = [s for s in required_sections if s.lower() not in txt.lower()]
        if missing:
            self.record_error(
                label,
                "Missing Sections",
                "README is missing required sections:\n- " + "\n- ".join(missing),
            )
        resources_block = re.search(
            r"(?is)(^#+\s*resources\b.*?)(^#+\s|\Z)",
            txt,
            re.MULTILINE,
        )
        if resources_block and "ai" not in resources_block.group(1).lower():
            self.record_error(
                label,
                "AI Usage Description",
                "Resources section must describe how AI was used in the project.",
            )
        required_topics = [
            "complete structure and format of your config file",
            "maze generation algorithm you chose",
            "why you chose this algorithm",
            "what part of your code is reusable, and how",
            "roles of each team member",
            "anticipated planning",
            "what worked well and what could be improved",
        ]
        for topic in required_topics:
            if topic.lower() not in txt.lower():
                self.record_error(
                    label,
                    "Required Content",
                    f"README should explicitly cover: '{topic}'.",
                )
                break
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")

    def test_reusable_module(self):
        label = "Reusable Module"
        console.print("\n[bold]Checking reusable mazegen module/package[/bold]")
        before = self._error_count(label)
        cwd = Path(os.getcwd())
        has_pkg_dir = (cwd / "mazegen" / "__init__.py").exists()
        dist_re = re.compile(r"^mazegen[-_].+\.(whl|tar\.gz)$")
        has_dist = any(
            p.is_file() and dist_re.match(p.name) for p in cwd.iterdir()
        )
        has_build_src = (cwd / "pyproject.toml").exists() or (cwd / "setup.py").exists()

        if not has_pkg_dir:
            self.record_error(
                label,
                "Missing Module",
                "Expected reusable module directory `mazegen/` with `__init__.py`.",
            )
        if not has_dist:
            self.warnings.append(
                "No `mazegen-*.whl` / `mazegen_*.whl` / `.tar.gz` artifact found at root yet "
                "(acceptable during development, but required for final submission)."
            )
        if not has_build_src:
            self.record_error(
                label,
                "Build Sources Missing",
                "Expected `pyproject.toml` or `setup.py` to rebuild the package during evaluation.",
            )

        if has_pkg_dir:
            try:
                tree = ast.parse((cwd / "mazegen" / "generator.py").read_text(encoding="utf-8"))
                has_class = any(
                    isinstance(n, ast.ClassDef) and n.name == "MazeGenerator"
                    for n in ast.walk(tree)
                )
                if not has_class:
                    self.record_error(
                        label,
                        "Missing Class",
                        "`mazegen/generator.py` should define class `MazeGenerator`.",
                    )
            except FileNotFoundError:
                self.record_error(label, "Missing File", "`mazegen/generator.py` not found.")
            except Exception as e:
                self.record_error(label, "Parse Error", f"Could not parse generator module: {e}")
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")

    def test_main_script_and_output(self):
        label = "Run & Output"
        console.print("\n[bold]Checking runtime and output format[/bold]")
        before = self._error_count(label)
        main_path = Path("a_maze_ing.py")
        cfg_path = Path("config.txt")
        if not main_path.exists() or not cfg_path.exists():
            return

        # Minimal style/type check using central checker (flake8 + mypy).
        style_errors = self.check_flake8(str(main_path))
        if style_errors:
            self.record_error(label, "Style Error", style_errors)
            console.print("[red]KO (style)[/red]")
            return

        run_cmd = [os.sys.executable, str(main_path), str(cfg_path)]
        try:
            result = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "TERM": "dumb"},
            )
        except subprocess.TimeoutExpired:
            self.warnings.append(
                "Runtime check timed out (likely interactive display); skipped strict run validation."
            )
            return
        except Exception as e:
            self.record_error(label, "Run Error", str(e))
            return

        # Some projects require an interactive TTY for curses/graphics; mark warning.
        combined = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0 and any(
            token in combined for token in ["nocbreak()", "curses", "terminal", "TERM"]
        ):
            self.warnings.append(
                "Runtime appears interactive-only in this terminal; output-format checks use existing output file."
            )

        # Validate output file format and maze consistency if available.
        cfg_txt = cfg_path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^\s*OUTPUT_FILE\s*=\s*(.+?)\s*$", cfg_txt, re.MULTILINE)
        width_m = re.search(r"^\s*WIDTH\s*=\s*(\d+)\s*$", cfg_txt, re.MULTILINE)
        height_m = re.search(r"^\s*HEIGHT\s*=\s*(\d+)\s*$", cfg_txt, re.MULTILINE)
        entry_m = re.search(r"^\s*ENTRY\s*=\s*(\d+)\s*,\s*(\d+)\s*$", cfg_txt, re.MULTILINE)
        exit_m = re.search(r"^\s*EXIT\s*=\s*(\d+)\s*,\s*(\d+)\s*$", cfg_txt, re.MULTILINE)
        perfect_m = re.search(r"^\s*PERFECT\s*=\s*(True|False)\s*$", cfg_txt, re.MULTILINE)
        if not m:
            self.record_error(label, "Config Error", "OUTPUT_FILE not found in config.txt")
            return
        if not (width_m and height_m and entry_m and exit_m and perfect_m):
            self.record_error(
                label,
                "Config Error",
                "Could not parse WIDTH/HEIGHT/ENTRY/EXIT/PERFECT from config.txt.",
            )
            return
        out_name = m.group(1).strip()
        width = int(width_m.group(1))
        height = int(height_m.group(1))
        entry = (int(entry_m.group(1)), int(entry_m.group(2)))
        exit_ = (int(exit_m.group(1)), int(exit_m.group(2)))
        perfect = perfect_m.group(1) == "True"
        out_path = Path(out_name)
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_name
        if not out_path.exists():
            self.record_error(
                label,
                "Missing Output",
                f"Expected output file `{out_path}` after run.",
            )
            return

        lines = out_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if "" not in lines:
            self.record_error(label, "Format Error", "Output file must contain an empty separator line.")
            return
        sep = lines.index("")
        grid = lines[:sep]
        trailer = lines[sep + 1 :]
        if len(trailer) != 3:
            self.record_error(
                label,
                "Format Error",
                "Output trailer must contain exactly 3 lines: ENTRY, EXIT, shortest path.",
            )
            return
        if not grid:
            self.record_error(label, "Format Error", "Hex grid section is empty.")
            return
        hex_re = re.compile(r"^[0-9A-Fa-f]+$")
        if any(not hex_re.match(row) for row in grid):
            self.record_error(label, "Format Error", "Grid rows must be hex digits only.")
        coord_re = re.compile(r"^\d+,\d+$")
        if not coord_re.match(trailer[0]) or not coord_re.match(trailer[1]):
            self.record_error(label, "Format Error", "ENTRY/EXIT lines must be `x,y` coordinates.")
        if not re.fullmatch(r"[NESW]*", trailer[2]):
            self.record_error(label, "Format Error", "Shortest path must only use letters N/E/S/W.")
        parsed = []
        for row in grid:
            parsed.append([int(c, 16) for c in row])
        if len(parsed) != height or any(len(r) != width for r in parsed):
            self.record_error(
                label,
                "Format Error",
                "Grid dimensions in output file do not match WIDTH/HEIGHT.",
            )
            console.print("[red]KO[/red]")
            return

        if trailer[0].replace(" ", "") != f"{entry[0]},{entry[1]}":
            self.record_error(label, "Format Error", "ENTRY line does not match config ENTRY.")
        if trailer[1].replace(" ", "") != f"{exit_[0]},{exit_[1]}":
            self.record_error(label, "Format Error", "EXIT line does not match config EXIT.")

        def is_closed(cell, direction):
            # bit mapping from subject: N=0 E=1 S=2 W=3
            return ((cell >> direction) & 1) == 1

        # Border walls must be closed.
        for x in range(width):
            if not is_closed(parsed[0][x], 0):
                self.record_error(label, "Maze Validity", "Top border cells must have North wall closed.")
                break
        for x in range(width):
            if not is_closed(parsed[height - 1][x], 2):
                self.record_error(label, "Maze Validity", "Bottom border cells must have South wall closed.")
                break
        for y in range(height):
            if not is_closed(parsed[y][0], 3):
                self.record_error(label, "Maze Validity", "Left border cells must have West wall closed.")
                break
        for y in range(height):
            if not is_closed(parsed[y][width - 1], 1):
                self.record_error(label, "Maze Validity", "Right border cells must have East wall closed.")
                break

        # Neighbor wall coherence.
        for y in range(height):
            for x in range(width):
                v = parsed[y][x]
                if y > 0 and is_closed(v, 0) != is_closed(parsed[y - 1][x], 2):
                    self.record_error(
                        label,
                        "Maze Coherence",
                        f"Incoherent N/S wall between ({x},{y}) and ({x},{y-1}).",
                    )
                    break
                if x < width - 1 and is_closed(v, 1) != is_closed(parsed[y][x + 1], 3):
                    self.record_error(
                        label,
                        "Maze Coherence",
                        f"Incoherent E/W wall between ({x},{y}) and ({x+1},{y}).",
                    )
                    break

        # No 3x3 fully open area.
        for y in range(height - 2):
            for x in range(width - 2):
                all_open = True
                for yy in range(y, y + 3):
                    for xx in range(x, x + 3):
                        if parsed[yy][xx] != 0:
                            all_open = False
                            break
                    if not all_open:
                        break
                if all_open:
                    self.record_error(
                        label,
                        "Maze Validity",
                        f"Forbidden 3x3 open area found near ({x},{y}).",
                    )
                    break

        moves = {"N": (0, -1, 0), "E": (1, 0, 1), "S": (0, 1, 2), "W": (-1, 0, 3)}

        def neighbors(x, y):
            v = parsed[y][x]
            out = []
            for d, (dx, dy, bit) in moves.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and not is_closed(v, bit):
                    out.append((nx, ny, d))
            return out

        # Connectivity check: subject allows isolated cells for the "42" pattern.
        # We tolerate disconnected cells only if they are fully closed (0xF).
        q = deque([(entry[0], entry[1])])
        seen = {(entry[0], entry[1])}
        while q:
            cx, cy = q.popleft()
            for nx, ny, _ in neighbors(cx, cy):
                if (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny))
        disconnected_open = []
        for y in range(height):
            for x in range(width):
                if (x, y) not in seen and parsed[y][x] != 0xF:
                    disconnected_open.append((x, y))
        if disconnected_open:
            self.record_error(
                label,
                "Maze Validity",
                "Maze has disconnected non-closed cells; only isolated fully closed pattern cells are tolerated.",
            )

        # Shortest path correctness from trailer.
        path = trailer[2].strip()
        cx, cy = entry
        path_ok = True
        for step in path:
            dx, dy, bit = moves[step]
            if is_closed(parsed[cy][cx], bit):
                path_ok = False
                break
            cx += dx
            cy += dy
            if not (0 <= cx < width and 0 <= cy < height):
                path_ok = False
                break
        if not path_ok or (cx, cy) != exit_:
            self.record_error(label, "Path Error", "Provided path is invalid or does not reach EXIT.")
        else:
            dist = {entry: 0}
            q2 = deque([entry])
            while q2:
                px, py = q2.popleft()
                for nx, ny, _ in neighbors(px, py):
                    if (nx, ny) not in dist:
                        dist[(nx, ny)] = dist[(px, py)] + 1
                        q2.append((nx, ny))
            shortest_len = dist.get(exit_)
            if shortest_len is None or len(path) != shortest_len:
                self.record_error(label, "Path Error", "Provided path is not a shortest valid path.")

        # PERFECT=True must imply unique path between entry and exit.
        # We evaluate this on the traversable component from ENTRY.
        if perfect:
            if seen:
                edge_count = 0
                for (x, y) in seen:
                    if x < width - 1 and (x + 1, y) in seen and not is_closed(parsed[y][x], 1):
                        edge_count += 1
                    if y < height - 1 and (x, y + 1) in seen and not is_closed(parsed[y][x], 2):
                        edge_count += 1
                nodes = len(seen)
                if edge_count != nodes - 1:
                    self.record_error(
                        label,
                        "Perfect Maze Error",
                        "PERFECT=True but traversable maze component is not a tree.",
                    )
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")

        self.test_seed_regeneration_behavior(main_path, cfg_path)

    def _extract_active_seed(self, cfg_text):
        for raw in cfg_text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip().upper() == "SEED":
                return value.strip()
        return None

    def _render_cfg_for_seed_test(self, cfg_text, output_file, seed_value):
        out_lines = []
        has_output = False
        has_seed = False
        for raw in cfg_text.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#") or "=" not in raw:
                out_lines.append(raw)
                continue
            key, _ = raw.split("=", 1)
            key_up = key.strip().upper()
            if key_up == "OUTPUT_FILE":
                out_lines.append(f"OUTPUT_FILE={output_file}")
                has_output = True
            elif key_up == "SEED":
                if seed_value is None:
                    out_lines.append(f"# {raw}")
                else:
                    out_lines.append(f"SEED={seed_value}")
                has_seed = True
            else:
                out_lines.append(raw)
        if not has_output:
            out_lines.append(f"OUTPUT_FILE={output_file}")
        if seed_value is not None and not has_seed:
            out_lines.append(f"SEED={seed_value}")
        return "\n".join(out_lines) + "\n"

    def _run_and_read_grid(self, main_path, cfg_text, output_path):
        with tempfile.NamedTemporaryFile("w", suffix=".cfg", delete=False) as cfg_tmp:
            cfg_tmp.write(cfg_text)
            cfg_tmp_path = Path(cfg_tmp.name)
        try:
            run_cmd = [os.sys.executable, str(main_path), str(cfg_tmp_path)]
            try:
                subprocess.run(
                    run_cmd,
                    capture_output=True,
                    text=True,
                    timeout=20,
                    env={**os.environ, "TERM": "dumb"},
                )
            except Exception:
                return None
            if not output_path.exists():
                return None
            lines = output_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if "" not in lines:
                return None
            sep = lines.index("")
            return lines[:sep]
        finally:
            try:
                cfg_tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    def test_seed_regeneration_behavior(self, main_path, cfg_path):
        label = "Seed Behavior"
        console.print("\n[bold]Checking SEED regeneration behavior[/bold]")
        before = self._error_count(label)
        cfg_txt = cfg_path.read_text(encoding="utf-8", errors="replace")
        active_seed = self._extract_active_seed(cfg_txt)
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            out_a = tmp_root / "maze_a.txt"
            out_b = tmp_root / "maze_b.txt"
            if active_seed is not None:
                try:
                    seed_a = int(active_seed)
                except ValueError:
                    self.record_error(label, "Seed Parse Error", "SEED must be an integer.")
                    console.print("[red]KO[/red]")
                    return
                cfg_a = self._render_cfg_for_seed_test(cfg_txt, str(out_a), seed_a)
                cfg_b = self._render_cfg_for_seed_test(cfg_txt, str(out_b), seed_a + 1)
                grid_a = self._run_and_read_grid(main_path, cfg_a, out_a)
                grid_b = self._run_and_read_grid(main_path, cfg_b, out_b)
                if grid_a is None or grid_b is None:
                    self.warnings.append(
                        "Could not complete SEED behavior runtime check in this environment."
                    )
                elif grid_a == grid_b:
                    self.record_error(
                        label,
                        "Seed Behavior Error",
                        "SEED is active but maze does not change when seed value changes.",
                    )
            else:
                cfg_a = self._render_cfg_for_seed_test(cfg_txt, str(out_a), None)
                cfg_b = self._render_cfg_for_seed_test(cfg_txt, str(out_b), None)
                grid_a = self._run_and_read_grid(main_path, cfg_a, out_a)
                grid_b = self._run_and_read_grid(main_path, cfg_b, out_b)
                if grid_a is None or grid_b is None:
                    self.warnings.append(
                        "Could not complete non-SEED determinism check in this environment."
                    )
                elif grid_a != grid_b:
                    self.record_error(
                        label,
                        "Seed Behavior Error",
                        "SEED is absent/commented, but maze changes between identical runs.",
                    )
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")

    def test_seed_interactive_regen_logic(self):
        label = "Seed Behavior"
        console.print("\n[bold]Checking interactive regen SEED logic[/bold]")
        before = self._error_count(label)
        display_path = Path("display.py")
        main_path = Path("a_maze_ing.py")
        if not display_path.exists():
            self.warnings.append(
                "Could not check interactive regen SEED logic (display.py not found)."
            )
            return
        try:
            txt = display_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            self.warnings.append(f"Could not read display.py for seed logic check: {e}")
            return

        # Strict AST validation:
        # "regen" branch seed increment must be guarded by
        # `seed_provided` (or explicit `seed is not None`) logic.
        try:
            tree = ast.parse(txt)
        except Exception as e:
            self.record_error(label, "Parse Error", f"Could not parse display.py: {e}")
            console.print("[red]KO[/red]")
            return

        loop_fn = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_loop":
                loop_fn = node
                break
        if loop_fn is None:
            self.record_error(label, "Missing Function", "display.py must define `_loop`.")
            console.print("[red]KO[/red]")
            return

        parent = {}
        for node in ast.walk(loop_fn):
            for child in ast.iter_child_nodes(node):
                parent[child] = node

        def _contains_name(node, name):
            return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(node))

        def _is_regen_if(node):
            if not isinstance(node, ast.If):
                return False
            cmp = node.test
            if not isinstance(cmp, ast.Compare):
                return False
            if not (isinstance(cmp.left, ast.Name) and cmp.left.id == "act"):
                return False
            if len(cmp.ops) != 1 or not isinstance(cmp.ops[0], ast.Eq):
                return False
            if len(cmp.comparators) != 1 or not isinstance(cmp.comparators[0], ast.Constant):
                return False
            return cmp.comparators[0].value == "regen"

        regen_if = next((n for n in ast.walk(loop_fn) if _is_regen_if(n)), None)
        if regen_if is None:
            self.record_error(
                label,
                "Missing Regen Branch",
                "Could not find `if act == \"regen\"` branch in display loop.",
            )
            console.print("[red]KO[/red]")
            return

        aug_targets = []
        for n in ast.walk(regen_if):
            if isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add) and isinstance(
                n.target, ast.Name
            ):
                aug_targets.append(n)

        guarded_ok = False
        for aug in aug_targets:
            cur = parent.get(aug)
            while cur is not None and cur is not regen_if:
                if isinstance(cur, ast.If):
                    # Accept guard either through explicit seed_provided variable
                    # or direct "seed is not None" condition.
                    if _contains_name(cur.test, "seed_provided"):
                        guarded_ok = True
                        break
                    if _contains_name(cur.test, "seed") and any(
                        isinstance(n, ast.Constant) and n.value is None
                        for n in ast.walk(cur.test)
                    ):
                        guarded_ok = True
                        break
                cur = parent.get(cur)
            if guarded_ok:
                break

        has_increment = len(aug_targets) > 0
        if has_increment and not guarded_ok:
            self.record_error(
                label,
                "Interactive Seed Logic Error",
                "Regen branch increments seed without a guard for missing/commented SEED.",
            )

        # Also validate seed forwarding in the bridge file:
        # launch(...) must receive the raw optional `seed`,
        # not a normalized fallback (e.g. effective_seed=42).
        if not main_path.exists():
            if self._error_count(label) == before:
                console.print("[green]OK[/green]")
            else:
                console.print("[red]KO[/red]")
            return
        try:
            main_txt = main_path.read_text(encoding="utf-8", errors="replace")
            main_tree = ast.parse(main_txt)
        except Exception:
            if self._error_count(label) == before:
                console.print("[green]OK[/green]")
            else:
                console.print("[red]KO[/red]")
            return

        bad_seed_forwarding = False
        for node in ast.walk(main_tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "launch":
                for kw in node.keywords:
                    if kw.arg == "seed":
                        if isinstance(kw.value, ast.Name):
                            if kw.value.id != "seed":
                                bad_seed_forwarding = True
                        else:
                            bad_seed_forwarding = True
        if bad_seed_forwarding:
            self.record_error(
                label,
                "Interactive Seed Logic Error",
                "When config SEED is commented/missing, UI regen must stay deterministic.\n"
                "Found invalid forwarding in `a_maze_ing.py`: `launch(seed=...)` is using a "
                "normalized/default value (for example `effective_seed`).\n"
                "Fix: pass the raw optional config seed to display: `launch(..., seed=seed, ...)`.\n"
                "Use fallback/default seed only for initial file generation, not for UI seed forwarding.",
            )
        if self._error_count(label) == before:
            console.print("[green]OK[/green]")
        else:
            console.print("[red]KO[/red]")
