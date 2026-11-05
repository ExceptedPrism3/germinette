"""Observe Codex scripts and caught errors in a separate interpreter."""

import json
import importlib.util
import os
import runpy
import sys
from pathlib import Path


def main():
    root = Path.cwd().resolve()
    script = Path(sys.argv[1]).resolve()
    data = {
        "lines": {},
        "calls": [],
        "errors": [],
        "reads": [],
        "dotenv": False,
        "imports": [],
        "versions": {},
        "exit": None,
        "configuration": [],
        "returns": [],
        "events": [],
    }
    keys = {
        "MATRIX_MODE",
        "DATABASE_URL",
        "API_KEY",
        "LOG_LEVEL",
        "ZION_ENDPOINT",
    }
    original_getitem = os._Environ.__getitem__
    if len(sys.argv) > 2:
        blocked = sys.argv[2]
        original_find_spec = importlib.util.find_spec

        def find_spec(name, package=None):
            if name.split(".")[0] == blocked:
                return None
            return original_find_spec(name, package)

        importlib.util.find_spec = find_spec

        class MissingReagent:
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split(".")[0] == blocked:
                    raise ModuleNotFoundError(
                        "Reagent deliberately unavailable: " + blocked,
                        name=fullname,
                    )

        sys.meta_path.insert(0, MissingReagent())

    def getitem(environ, key):
        try:
            value = original_getitem(environ, key)
        except KeyError:
            value = None
            raise
        finally:
            frame = sys._getframe(1)
            while frame:
                if "dotenv" in Path(frame.f_code.co_filename).parts:
                    break
                if str(frame.f_code.co_filename).startswith(
                    str(root) + os.sep
                ):
                    if key in keys:
                        data["reads"].append([key, value])
                    break
                frame = frame.f_back
        return value

    def trace(frame, event, arg):
        filename = frame.f_code.co_filename
        name = frame.f_code.co_name
        if event == "call":
            if name in ("load_dotenv", "dotenv_values") and (
                "dotenv" in Path(filename).parts
            ):
                data["dotenv"] = True
            if name == "_find_and_load":
                data["imports"].append(frame.f_locals.get("name"))
        if filename.startswith(str(root) + os.sep):
            relative = Path(filename).relative_to(root).as_posix()
            if event == "line":
                data["lines"].setdefault(relative, []).append(frame.f_lineno)
                for value in tuple(frame.f_locals.values()):
                    if isinstance(value, dict) and keys <= value.keys():
                        config = {key: value[key] for key in keys}
                        if all(
                            isinstance(item, (str, type(None)))
                            for item in config.values()
                        ):
                            if config not in data["configuration"]:
                                data["configuration"].append(config)
            elif event == "call":
                data["calls"].append([relative, name])
                data["events"].append(["call", relative, name])
            elif event == "return" and isinstance(arg, str):
                data["returns"].append([relative, name, arg])
            elif event == "exception":
                data["events"].append(
                    ["exception", relative, frame.f_lineno, arg[0].__name__]
                )
                data["errors"].append(
                    [relative, frame.f_lineno, arg[0].__name__, str(arg[1])]
                )
        return trace

    # run_path omits the script folder that normal invocation adds.
    sys.path.insert(0, str(script.parent))
    os._Environ.__getitem__ = getitem
    sys.settrace(trace)
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as error:
        if error.code not in (None, 0):
            data["exit"] = ["SystemExit", str(error.code)]
    except BaseException as error:
        data["exit"] = [type(error).__name__, str(error)]
    finally:
        sys.settrace(None)
        os._Environ.__getitem__ = original_getitem
        for name in ("pandas", "numpy"):
            module = sys.modules.get(name)
            if module is not None:
                data["versions"][name] = str(
                    getattr(module, "__version__", "")
                )
        print("\nGERMINETTE_TRACE=" + json.dumps(data), file=sys.stderr)


if __name__ == "__main__":
    main()
