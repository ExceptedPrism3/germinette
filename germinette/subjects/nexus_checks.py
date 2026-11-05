"""Behavior contracts shared by the two supplied Code Nexus subjects."""

PROCESSORS = """
import inspect
assert inspect.isabstract(DataProcessor), "DataProcessor must be abstract"
assert {"validate", "ingest"} <= DataProcessor.__abstractmethods__
assert "output" not in DataProcessor.__abstractmethods__
for cls, batches, expected, invalid in (
    (NumericProcessor, [42, [1, 2.5], -3.5],
     ["42", "1", "2.5", "-3.5"], ["bad", [1, "bad"], {}]),
    (TextProcessor, ["alpha", ["beta", "gamma"]],
     ["alpha", "beta", "gamma"], [42, ["ok", 42], {}]),
    (LogProcessor, [{"log_level": "INFO", "log_message": "first"},
                    [{"log_level": "ERROR", "log_message": "second"}]],
     ["first", "second"], [42, "bad", [{"key": 42}]]),
):
    assert issubclass(cls, DataProcessor)
    processor = cls()
    for data in invalid:
        assert processor.validate(data) is False, (cls.__name__, data)
        try:
            processor.ingest(data)
        except Exception:
            pass
        else:
            raise AssertionError(f"{cls.__name__}.ingest must reject {data!r}")
    for batch in batches:
        assert processor.validate(batch) is True, (cls.__name__, batch)
        processor.ingest(batch)
    outputs = [processor.output() for _ in expected]
    assert all(isinstance(item, tuple) and len(item) == 2
               and type(item[0]) is int and isinstance(item[1], str)
               for item in outputs), "output must return (int, str)"
    ranks = [item[0] for item in outputs]
    assert ranks == list(range(ranks[0], ranks[0] + len(ranks)))
    for item, value in zip(outputs, expected):
        matches = (value in item[1] if cls is LogProcessor
                   else item[1] == value)
        assert matches, (cls.__name__, outputs, expected)
"""

STREAM = """
import contextlib
import io
stream = DataStream()
numeric, text, logs = NumericProcessor(), TextProcessor(), LogProcessor()
for processor in (numeric, text, logs):
    stream.register_processor(processor)
captured = io.StringIO()
with contextlib.redirect_stdout(captured):
    stream.process_stream([42, [1, 2.5], "hello", ["world"],
                           {"log_level": "INFO", "log_message": "test"},
                           object()])
assert captured.getvalue().strip(), "Report unprocessable stream elements"
assert [numeric.output()[1] for _ in range(3)] == ["42", "1", "2.5"]
assert [text.output()[1] for _ in range(2)] == ["hello", "world"]
assert "test" in logs.output()[1]
stream.print_processors_stats()
# A new processor must work without modifying DataStream's type dispatch.
class CustomProcessor(DataProcessor):
    def __init__(self): self.received = []
    def validate(self, data): return data is marker
    def ingest(self, data): self.received.append(data)
marker = object()
custom = CustomProcessor()
stream.register_processor(custom)
stream.process_stream([marker])
assert custom.received == [marker], "Route by validate(), not concrete type"
"""

PIPELINE = """
assert getattr(ExportPlugin, '_is_protocol', False), 'Use a Protocol'
class Plugin:
    def __init__(self): self.received = []
    def process_output(self, data): self.received.extend(data)
stream = DataStream()
for processor in (NumericProcessor(), TextProcessor()):
    stream.register_processor(processor)
stream.process_stream([[10, 20, 30], ["alpha", "beta"]])
plugin = Plugin()
stream.output_pipeline(2, plugin)
assert sorted(item[1] for item in plugin.received) == [
    "10", "20", "alpha", "beta"]
assert all(isinstance(item, tuple) and len(item) == 2
           and type(item[0]) is int and isinstance(item[1], str)
           for item in plugin.received)
remaining = Plugin()
stream.output_pipeline(10, remaining)
assert [item[1] for item in remaining.received] == ["30"], "Consume once"

# Check formats without imposing plugin class names.
import contextlib
import csv
import inspect
import io
import json
sample = [(0, 'comma,value'), (1, 'quote"value'), (2, 'plain')]
expected = [item[1] for item in sample]
formats = set()
for candidate in list(globals().values()):
    if (not inspect.isclass(candidate) or candidate is ExportPlugin
            or not callable(getattr(candidate, 'process_output', None))):
        continue
    try:
        inspect.signature(candidate).bind()
    except (TypeError, ValueError):
        continue
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        candidate().process_output(sample)
    for line in captured.getvalue().splitlines():
        try:
            if next(csv.reader([line])) == expected:
                formats.add('csv')
        except (csv.Error, StopIteration):
            pass
        try:
            payload = json.loads(line)
        except (ValueError, TypeError):
            continue
        values = (list(payload.values())
                  if isinstance(payload, dict) else payload)
        if values == expected:
            formats.add('json')
assert formats == {'csv', 'json'}, 'Produce valid, escaped CSV and JSON'
"""


def intentional_ingest_errors(tree):
    """Allow the PDF's deliberate type error only in guarded demo calls."""
    import ast

    return [
        (call.lineno, "arg-type")
        for node in tree.body
        if not isinstance(node, ast.ClassDef)
        for block in ast.walk(node)
        if isinstance(block, ast.Try)
        for call in ast.walk(block)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "ingest"
    ]
