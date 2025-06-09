from setup import BuildExtOptimized, game_files  # type: ignore

from setuptools import setup  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    cmdclass={"build_ext": BuildExtOptimized},
    options={"build_ext": {"parallel": 8}},
    ext_modules=mypycify(["utils.py", "fen_utils.py"] + game_files),
)
