from abc import ABC, abstractmethod

class Bot(ABC):
    @abstractmethod
    def generate_move(self, game_state, allotted_time: float = 3, depth: int = -1) -> tuple[tuple[int, tuple[int, int, int, int]], int]:
        ...

    @abstractmethod
    def clear_cache(self) -> None:
        ...
