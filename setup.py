#!/usr/bin/env python

from setuptools import setup, find_packages
from io import open

# Version info -- read without importing
_locals = {}
with open("pytest_relaxed/_version.py") as fp:
    exec(fp.read(), None, _locals)
version = _locals["__version__"]


setup(
    name="pytest-relaxed",
    version=version,
    description="Relaxed test discovery/organization for pytest",
    license="BSD",
    url="https://pytest-relaxed.readthedocs.io/",
    author="Jeff Forcier",
    author_email="jeff@bitprophet.org",
    long_description="\n" + open("README.rst", encoding="utf-8").read(),
    packages=find_packages(),
    entry_points={
        # TODO: do we need to name the LHS 'pytest_relaxed' too? meh
        "pytest11": ["relaxed = pytest_relaxed.plugin"]
    },
    install_requires=["pytest>=3,<5", "six>=1,<2", "decorator>=4,<5"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
)
