# setup.py
from setuptools import setup  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        ["game_handling.py", "utils.py", "game.py", "main.py", "fen_utils.py", "bot_v1.py", "bot_v4.py",
         "bot_v2.py", "bot_v3_5.py", "bot_v3_6.py", "bot_v3_7.py", "bot_v4_2.py"],
        opt_level="3",
        debug_level="1",
        strict_dunder_typing=False
    ),
)