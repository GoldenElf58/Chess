from setup import BuildExtOptimized

from setuptools import setup  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore
from mypyc.build import mypycify


setup(
    name="Chess",
    cmdclass={"build_ext": BuildExtOptimized},
    options={"build_ext": {"parallel": 8}},
    ext_modules=mypycify(
        ["utils.py", "fen_utils.py", "correct_game_v2.py", "game_format_v2.py", "game_base.py",
         "game.py", "game_bitboards.py", "game_bitboards_v2.py", "game_v2.py", "game_v3.py"]
    ),
)