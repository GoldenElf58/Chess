def split_table(flat_list: tuple) -> tuple:
    """Converts a flat list of 64 numbers into an 8x8 2D list."""
    return tuple([flat_list[i * 8:(i + 1) * 8] for i in range(8)])


def flatten(board) -> tuple:
    return tuple([x for row in board for x in row])

# For black pieces, we mirror the white table vertically.
def mirror(table: tuple, flattened=True) -> tuple:
    """Mirrors an 8x8 table vertically."""
    if flattened:
        return flatten(split_table(table)[::-1])
    return table[::-1]

def negate(lst: tuple[int, ...]) -> tuple[int, ...]:
    return tuple([-x for x in lst])

