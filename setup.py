#!/usr/bin/env python

import os.path
import sys

from setuptools import setup, find_packages


def read(*filenames):
    """Read files relative to the executable."""
    files = []
    for filename in filenames:
        full_path = os.path.join(os.path.dirname(sys.argv[0]), filename)
        with open(full_path, 'r') as fh:
            files.append(fh.read())
    return "\n\n".join(files)


setup(
    name='adjunct',
    version='0.1.1',
    description='Sundry libraries',
    long_description=read('README'),
    url='https://github.com/kgaughan/adjunct/',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    zip_safe=True,

    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ),

    author='Keith Gaughan',
    author_email='k@stereochro.me',
)
