from setuptools import setup, find_packages
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

def utf8_open(*path_parts):
    return open(path.join(*path_parts), encoding='utf-8')

def find_version(*path_parts):
    with utf8_open(*path_parts) as f:
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]",
            f.read(), re.M
        )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")

setup(
    name='ngcloud',
    version=find_version('ngcloud', '__init__.py'),

    license='MIT',
    description='NGCloud result parser',

    author='Liang Bo Wang',
    author_email='r02945054@ntu.edu.tw',

    url='https://github.com/ccwang002/ngcloud',
    classifiers=[
        'Development Status :: 3 - Beta',
    ],

    entry_points={
        'console_scripts': [
            'ngparse = ngcloud.parser:main',
        ],
    },

    install_requires=[
        'docopt > 0.6',
        'PyYAML',
    ],

    keywords='ngs',
    packages=find_packages(
        exclude=['contrib', 'docs', 'test*']
    ),
    test_suite='nose.collector',
)
