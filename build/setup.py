from setuptools import setup  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        ["utils.py", "fen_utils.py", "game.py", "game_bitboards.py", "game_bitboards_v2.py", "game_v2.py"],
    ),
)
