#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pytest-relaxed',
    version='0.0.1',
    description='Relaxed test discovery/organization for pytest',
    license='BSD',

    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',

    packages=find_packages(),
    entry_points={
        # TODO: do we need to name the LHS 'pytest_relaxed' too? meh
        'pytest11': ['relaxed = pytest_relaxed'],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
)
