#!/usr/bin/env python3

from setuptools import setup, find_packages


with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

setup(
    name='twitterscraper',
    version='0.2.4',
    description='Tool for scraping Tweets',
    url='https://github.com/taspinar/twitterscraper',
    author=['Ahmet Taspinar', 'Lasse Schuirmann'],
    author_email='taspinar@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["build.*", "tests", "tests.*"]),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "TwitterScraper = twitterscraper.main:main"
        ]
    })
