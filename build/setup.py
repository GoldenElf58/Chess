from setuptools import setup  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        ["game_handling.py", "utils.py", "main.py", "fen_utils.py", "game.py", "game_bitboards.py", "game_v2.py"],
    ),
)
