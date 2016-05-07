from setuptools import setup

setup(
    name='sqlite2json',
    version='1.0.1',
    author='John Gerlock',
    author_email='john@pikkey.com',
    packages=['sqlite2json'],
    url='https://github.com/john-g-g/sqlite2json',
    license=open('LICENSE').read(),
    description='SQLite to JSON converter',
    long_description=open('README.md').read(),
    entry_points = {
        'console_scripts': [
            'sqlite2json = sqlite2json:main'
        ]
    }
)
