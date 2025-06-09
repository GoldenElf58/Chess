from setuptools import setup  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore
from mypyc.build import mypycify
import glob

# collect all .py files in bots/
bot_files = glob.glob("bots/*.py")

class BuildExtOptimized(build_ext):
    def build_extensions(self):
        # apply flags to every extension
        for ext in self.extensions:
            ext.extra_compile_args = [
                "-O3",
                "-march=native",
                "-Wno-unused-variable",
                "-Wno-unused-function",
                "-Wno-unused-label",
                "-Wno-unreachable-code"
            ]
        super().build_extensions()

setup(
    name="Chess",
    cmdclass={"build_ext": BuildExtOptimized},
    ext_modules=mypycify(
        ["utils.py", "fen_utils.py", "correct_game_v2.py", "game_format_v2.py", "game_base.py",
         "game.py", "game_bitboards.py", "game_bitboards_v2.py", "game_v2.py", "game_v3.py"]
        + bot_files
    ),
)