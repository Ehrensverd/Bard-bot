from os import path
from codecs import open
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

AUTHOR = "Eskil Oscar Ehrensvärd"
URL = "https://github.com/Ehrensverd/Bard-bot"

pkg_info_template = f"""
# coding: utf-8
# file generated by setuptools_scm
# don't change, don't track in version control
__author__ = '{AUTHOR}'
__homepage__ = '{URL}'
__version__ = '{{version}}'
"""

setup(
    name="bardbot",
    use_scm_version={
        "write_to": "src/bardbot/_pkg_info.py",
        "write_to_template": pkg_info_template,
    },
    description="Bard-bot: the perfect sound kit for your DM adventures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    author=AUTHOR,
    author_email="mail.eskil@gmail.com",
    license="BSD 3-Clause",
    classifiers=[
        "Development Status :: 3 - Alpha",
        # "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="DnD Discord Bot Soundboard DM",
    setup_requires=[
        "setuptools_scm>=1.7",
        "wheel",
    ],
    install_requires=[
        "bringbuf",  # FIXME: TEMP
        "ffmpeg",  # FIXME: TEMP
        "python-dotenv",  # FIXME: TEMP
        "PyNaCl",
        "beautifulsoup4",
        "discord.py",
        "requests",
        "pydub",
    ],
    entry_points={
        "console_scripts": [
            "bardbot=bardbot.bot:main",
        ],
    },
    python_requires=">=3.6",
)
