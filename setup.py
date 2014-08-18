import sys
import re
import subprocess as sp
from os import path, walk, environ
from glob import glob
from setuptools import setup, find_packages, Command
from codecs import open

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

def _build_frontend():
    p = sp.Popen("gulp release", cwd="template_dev", shell=True)
    p.wait()
    if p.returncode:
        sys.exit("Building CSS/JS fails, "
                 "try `npm install` under template_dev/")

def _check_frontend_build():
    print("Checking if all generated CSS/JSs exist")
    frontend_patterns = [
        'ngcloud/pipe/report/shared/static/css/*.css'
    ]
    all_built = all(any(glob(pattern)) for pattern in frontend_patterns)
    if not all_built:
        print("Some built CSS/JSs are missing, rebuild all")
        _build_frontend()


class build_frontend(Command):
    description = (
        'build CSS/JS from Stylus/Coffeescript, '
        'Node.js dev environment required'
    )
    user_options = [
        ("skip-if-exist", None, "skip whole building if files exist")
    ]

    def initialize_options(self):
        self.skip_if_exist = None

    def finalize_options(self):
        pass

    def run(self):
        if self.skip_if_exist:
            on_rtd = environ.get('READTHEDOCS', None) == 'True'
            if on_rtd:
                print("on ReadtheDocs, skip building")
                return
            _check_frontend_build()
        else:
            print("rebuilding all generated CSS/JSs")
            _build_frontend()


with utf8_open("README.rst") as readme_f:
    with utf8_open("CHANGES.rst") as changes_f:
        long_description = readme_f.read() + '\n' + changes_f.read()

# recursively find all files under ngcloud/pipe/report
pipe_template_data = [
    path.relpath(path.join(root, f), 'ngcloud/pipe')
    for root, _, files in walk('ngcloud/pipe/report')
    for f in files
]

# define pacakge dependencies
pkg_deps = ['docopt > 0.6', 'PyYAML', 'Jinja2 > 2']
if sys.version_info[:2] < (3, 4):
    pkg_deps.append('pathlib')

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
    long_description=long_description,

    author='Liang Bo Wang',
    author_email='r02945054@ntu.edu.tw',

    url='https://github.com/BioCloud-TW/ngcloud',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='ngs',

    cmdclass={
        'build_frontend': build_frontend,
    },

    install_requires=pkg_deps,
    extras_require={
        'color': color_dep,
        'all': all_dep,
    },

    packages=find_packages(
        exclude=[
            'contrib', 'docs', 'examples',
            '*.tests', '*.tests.*', 'tests.*', 'tests',
        ]
    ),
    package_data={
        'ngcloud.pipe': pipe_template_data,
    },
    zip_safe=False,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'ngreport = ngcloud.report:main',
        ],
    },

)
