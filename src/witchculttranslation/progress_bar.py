from abc import abstractmethod
from typing import Protocol, Self


class ProgressBar(Protocol):
    @abstractmethod
    def __enter__(self) -> Self: ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @abstractmethod
    def update(self, size: int) -> None: ...
