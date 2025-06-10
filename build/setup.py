from setuptools import setup  # type: ignore
from setuptools.command.build_ext import build_ext  # type: ignore
from mypyc.build import mypycify
import glob
import time

# collect all .py files in bots/
bot_files = glob.glob("bots/*.py")
game_files = glob.glob("game_states/*.py")


class BuildExtOptimized(build_ext):
    def run(self):
        start = time.time()
        super().run()
        duration = time.time() - start
        print(f"Compilation completed in {duration:.2f} seconds")

    def build_extensions(self):
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
    ext_modules=mypycify(["utils.py", "fen_utils.py"] + bot_files + game_files),
)
