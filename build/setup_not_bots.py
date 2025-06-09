from setuptools import setup  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore
from mypyc.build import mypycify
import time


class BuildExtOptimized(build_ext):
    def run(self):
        start = time.time()
        super().run()
        duration = time.time() - start
        print(f"Compilation completed in {duration:.2f} seconds")

    def build_extensions(self):
        # apply flags to every extension
        for ext in self.extensions:
            ext.extra_compile_args = [
                "-O3",
                "-g0",
                "-march=native",
                "-Wno-unused-variable",
                "-Wno-unused-function",
                "-Wno-unused-label",
                "-Wno-unreachable-code",
                "-Wno-unused-but-set-variable",
            ]
        super().build_extensions()

setup(
    name="Chess",
    cmdclass={"build_ext": BuildExtOptimized},
    options={"build_ext": {"parallel": 8}},
    ext_modules=mypycify(
        ["utils.py", "fen_utils.py", "correct_game_v2.py", "game_format_v2.py", "game_base.py",
         "game.py", "game_bitboards.py", "game_bitboards_v2.py", "game_v2.py", "game_v3.py"]
    ),
)