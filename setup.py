#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name='twitterscraper',
    version='0.2.1',
    description='Tool for scraping Tweets',
    url='https://github.com/taspinar/twitterscraper',
    author=['Ahmet Taspinar', 'Lasse Schuirmann'],
    author_email='taspinar@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["build.*", "tests", "tests.*"]),
    install_requires=[
        'bs4', 'lxml', 'fake_useragent'
    ],
    entry_points={
        "console_scripts": [
            "TwitterScraper = twitterscraper.main:main"
        ]
    })
