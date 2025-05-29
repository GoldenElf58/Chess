# setup.py
from setuptools import setup  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        ["game_handling.py", "utils.py", "game.py", "main.py", "fen_utils.py", "game_bitboards.py", "game_v2.py"],
        opt_level="3",
        debug_level="1",
        strict_dunder_typing=False
    ),
)