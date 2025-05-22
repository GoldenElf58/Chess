# setup.py
from setuptools import setup
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        ["game_handling.py", "bot_v1.py", "utils.py", "game.py", "main.py", "fen_utils.py"],  # add more .py files here
        opt_level="3",
        debug_level="1",
        strict_dunder_typing=False
    ),
)