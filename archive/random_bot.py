from bots.bot import Bot


class RandomBot(Bot):
    def generate_move(self, game_state, allotted_time=3, depth=-1) -> tuple[tuple[int, tuple[int, int, int, int]], int]:
        return (0, game_state.get_moves()[0]), 0

    def clear_cache(self):
        pass
