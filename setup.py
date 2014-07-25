from setuptools import setup, find_packages
from codecs import open
from os import path
from pathlib import Path
import re
import sys

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

# recursively find all files under ngcloud/pipe/report
pipe_template_data = [
    p.relative_to('ngcloud/pipe').as_posix()
    for p in Path('ngcloud/pipe/report').glob("**/*")
    if not p.is_dir()
]

if sys.platform.startswith("win32"):
    color_dep = ['colorlog[windows]']
else:
    color_dep = ['colorlog']

all_dep = []
for deps in [color_dep]:
    all_dep.extend(deps)

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
    keywords='ngs',

    install_requires=[
        'docopt > 0.6',
        'PyYAML',
        'Jinja2 > 2',
    ],
    extras_require={
        'color': color_dep,
        'all': all_dep,
    },

    packages=find_packages(
        exclude=['contrib', 'docs', 'test*']
    ),
    package_data={
        'ngcloud.pipe': pipe_template_data,
    },
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'ngreport = ngcloud.report:main',
        ],
    },

)
