#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt', 'r') as requirements_file:
    requirements_txt = requirements_file.readlines()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
] + requirements_txt

setup_requirements = [
    # TODO(mofe23): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='fluke_28x_multimeter',
    version='0.1.0',
    description="SteadySense Fluke 28x Multimeter implementation",
    long_description=readme + '\n\n' + history,
    author="Moritz Federspiel",
    author_email='moritz.federspiel@steadysense.at',
    url='https://github.com/mofe23/fluke_28x_multimeter',
    packages=find_packages(include=['fluke_28x_multimeter']),
    entry_points={
        'console_scripts': [
            'fluke=fluke_28x_multimeter.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='fluke_28x_multimeter',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
