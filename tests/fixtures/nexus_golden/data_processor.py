"""Typed processors; the intentional invalid ingestion remains in the demo."""

from abc import ABC, abstractmethod
from typing import Any


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


def processor_demo() -> None:
    print('=== Code Nexus - Data Processor ===')
    cases: list[tuple[DataProcessor, Any]] = [
        (NumericProcessor(), [1, 2.5]),
        (TextProcessor(), ['Hello', 'World']),
        (LogProcessor(), [{'log_level': 'INFO', 'log_message': 'ready'}]),
    ]
    for processor, values in cases:
        print(processor.__class__.__name__.replace('Processor', ' Processor'))
        print(processor.validate(values))
        processor.ingest(values)
        print(processor.output())
    numeric = NumericProcessor()
    try:
        numeric.ingest('foo')
    except ValueError as exc:
        print('Got exception:', exc)


if __name__ == '__main__':
    processor_demo()
