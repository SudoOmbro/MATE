import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="mate-wrapper",
    version="1.1.0",
    description="The Easy Telegram Application Maker",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/SudoOmbro/MATE",
    author="SudoOmbro",
    author_email="ombroso1000@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9"
    ],
    packages=["MateWrapper", "MateMenus"],
    include_package_data=True,
    install_requires=["python-telegram-bot"]
)