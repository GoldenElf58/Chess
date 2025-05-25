from typing import Sequence, cast, Any
from numbers import Real


def split_table[T](flat_list: Sequence[T]) -> tuple[tuple[T, ...], ...]:
    """Converts a flat list of 64 numbers into an 8x8 2D tuple."""
    return tuple(tuple(flat_list[i * 8:(i + 1) * 8]) for i in range(8))


def flatten[T](board: Sequence[Sequence[T]]) -> tuple[T, ...]:
    """Flattens a 2D list into a 1D tuple."""
    return tuple([x for row in board for x in row])

# For black pieces, we mirror the white table vertically.
def mirror(table: tuple[int, ...], flattened: bool = True) -> tuple[int, ...]:
    """Mirrors an 8x8 table vertically."""
    if flattened:
        return flatten(split_table(table)[::-1])
    return table[::-1]

def negate(lst: Sequence[int]) -> tuple[int, ...]:
    return tuple(-x for x in lst)
