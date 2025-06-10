from abc import ABC, abstractmethod
from typing import Any


class Bot(ABC):
    @abstractmethod
    def generate_move(self, game_state, allotted_time: float = 3, depth: int = -1) -> tuple[tuple[int, Any], int]:
        ...

    @abstractmethod
    def clear_cache(self) -> None:
        ...

    @classmethod
    def get_version(cls):
        return cls.__name__
