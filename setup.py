#!/usr/bin/env python

from setuptools import setup, find_packages
from adjunct.buildkit import *


META = get_metadata('adjunct/__init__.py')


setup(
    name='adjunct',
    version=META['version'],
    description='Sundry libraries',
    long_description=read('README'),
    url='https://github.com/kgaughan/adjunct/',
    license='MIT',
    packages=find_packages(exclude='tests'),
    zip_safe=True,
    install_requires=read_requirements('requirements.txt'),

    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ),

    author=META['author'],
    author_email=META['email'],
)
