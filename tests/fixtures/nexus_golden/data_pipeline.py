"""Typed processors; the intentional invalid ingestion remains in the demo."""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class DataProcessor(ABC):
    def __init__(self) -> None:
        self.items: list[str] = []
        self.rank = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        result = self.rank, self.items.pop(0)
        self.rank += 1
        return result


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, list):
            return all(isinstance(item, (int, float)) for item in data)
        return isinstance(data, (int, float))

    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise ValueError('Improper numeric data')
        values = data if isinstance(data, list) else [data]
        self.items.extend(str(value) for value in values)


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, list):
            return all(isinstance(item, str) for item in data)
        return isinstance(data, str)

    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise ValueError('Improper text data')
        self.items.extend(data if isinstance(data, list) else [data])


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, list):
            return all(self.validate(item) and isinstance(item, dict)
                       for item in data)
        return isinstance(data, dict) and all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in data.items())

    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise ValueError('Improper log data')
        values = data if isinstance(data, list) else [data]
        self.items.extend(f'{item["log_level"]}: {item["log_message"]}'
                          for item in values)


class ExportPlugin(Protocol):
    def process_output(self, data: list[tuple[int, str]]) -> None:
        ...


class CSVPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        print('CSV Output:')
        print(','.join('"' + value.replace('"', '""') + '"'
                       for _, value in data))


class JSONPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        print('JSON Output:')
        escaped = [(rank, value.replace('\\', '\\\\').replace('"', '\\"'))
                   for rank, value in data]
        print('{' + ', '.join(f'"item_{rank}": "{value}"'
                              for rank, value in escaped) + '}')


class DataStream:
    def __init__(self) -> None:
        self.processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self.processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        for item in stream:
            for processor in self.processors:
                if processor.validate(item):
                    processor.ingest(item)
                    break
            else:
                print('Cannot process:', item)

    def print_processors_stats(self) -> None:
        print('== DataStream statistics ==')
        for processor in self.processors:
            print(processor.__class__.__name__, processor.rank,
                  'consumed;', len(processor.items), 'remaining')

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for processor in self.processors:
            result = []
            for _ in range(nb):
                try:
                    result.append(processor.output())
                except IndexError:
                    break
            plugin.process_output(result)


if __name__ == '__main__':
    print('=== Code Nexus - Data Pipeline ===')
    ds = DataStream()
    ds.register_processor(NumericProcessor())
    ds.process_stream([1, 2, 3])
    ds.print_processors_stats()
    ds.output_pipeline(2, CSVPlugin())
    ds.output_pipeline(2, JSONPlugin())
