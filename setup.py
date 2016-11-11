from setuptools import setup, find_packages

setup(
    name='twitterscraper',
    version='0.2.0',
    description='Tool for scraping Tweets',
    url='https://github.com/taspinar/twitterscraper',
    author='Ahmet Taspinar',
    author_email='taspinar@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["build.*", "tests", "tests.*"]),
    install_requires=[
        'bs4', 'lxml', 'fake_useragent'
    ])
