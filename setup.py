from setuptools import setup

setup(
    name="pyls",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pyls = pyls:main",
        ],
    },
)
