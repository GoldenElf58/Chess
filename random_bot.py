class Bot:
    @staticmethod
    def generate_move(game_state, allotted_time=3, depth=-1) -> tuple[tuple[int, tuple[int, int, int, int]], int]:
        return (0, game_state.get_moves()[0]), 0

    @staticmethod
    def clear_cache():
        pass
