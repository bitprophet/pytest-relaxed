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
    project_urls={
        "Source": "https://github.com/bitprophet/pytest-relaxed",
        "Changelog": "https://github.com/bitprophet/pytest-relaxed/blob/main/docs/changelog.rst",  # noqa
        "CI": "https://app.circleci.com/pipelines/github/bitprophet/pytest-relaxed",  # noqa
    },
    author="Jeff Forcier",
    author_email="jeff@bitprophet.org",
    long_description="\n" + open("README.rst", encoding="utf-8").read(),
    packages=find_packages(),
    entry_points={
        # TODO: do we need to name the LHS 'pytest_relaxed' too? meh
        "pytest11": ["relaxed = pytest_relaxed.plugin"]
    },
    python_requires=">=3.6",
    install_requires=[
        # Difficult to support Pytest<7 + Pytest>=7 at same time, and
        # pytest-relaxed never supported pytests 5 or 6, so...why bother!
        "pytest>=7",
        # For @raises, primarily. At press time, most available decorator
        # versions (including 5.x) should work for us / our Python interpreter
        # versions.
        "decorator",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
    ],
)
