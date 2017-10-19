#!/usr/bin/env python

from setuptools import setup, find_packages


# Version info -- read without importing
_locals = {}
with open('pytest_relaxed/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']


setup(
    name='pytest-relaxed',
    version=version,
    description='Relaxed test discovery/organization for pytest',
    license='BSD',

    url="https://github.com/bitprophet/pytest-relaxed",
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    long_description="\n" + open('README.rst').read(),

    packages=find_packages(),
    entry_points={
        # TODO: do we need to name the LHS 'pytest_relaxed' too? meh
        'pytest11': ['relaxed = pytest_relaxed.plugin'],
    },

    install_requires=[
        # TODO: is it worth tightening/loosening this? At the moment I don't
        # know of any specific pytest releases/bugs/features that limit me
        # besides presumable major version API compat concerns.
        'pytest>=3,<4',
        # TODO: ditto; six is so widely used it's prob worth having a broad pin
        'six>=1,<2',
        # TODO: ditto again!
        # TODO: but also, we could make this optional if it somehow ever caused
        # issues for anyone. Only necessary for @raises right now.
        'decorator>=4,<5',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
)
