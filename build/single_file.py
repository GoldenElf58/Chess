from setuptools import setup  # type: ignore
from mypyc.build import mypycify

setup(
    name="Chess",
    ext_modules=mypycify(
        [
            # "bots/bot_v5_3.py",
            "bots/bot_v5_4.py",
            # "bots/__init__.py",
         ]
    ),
)
