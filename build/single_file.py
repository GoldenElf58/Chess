from setuptools import setup  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        [
            # "game_v3.py",
            # "game_v2.py",
            "bots/bot_v1.py",
            # "bots/bot_v5_3.py",
            # "bots/bot_v5_4.py",
            # "bots/__init__.py",
         ]
    ),
)
