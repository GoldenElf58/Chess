def split_table(flat_list):
    """Converts a flat list of 64 numbers into an 8x8 2D list."""
    return [flat_list[i * 8:(i + 1) * 8] for i in range(8)]


def flatten(board):
    return [x for row in board for x in row]

# For black pieces, we mirror the white table vertically.
def mirror(table, flattened=True):
    """Mirrors an 8x8 table vertically."""
    if flattened:
        return flatten(split_table(table)[::-1])
    return table[::-1]

def negate(lst):
    return [-x for x in lst]

