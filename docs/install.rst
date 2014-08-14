Installation
============

Require Python 3.3+, setuptools, and pip. Other Python versions have not been tested.

On versions below 3.4, pathlib_ is required during installation. Install it through

.. code::

    pip install pathlib

before installation

.. note:: Python 3.4+ should come along with setuptools and pip, but that's not always the case on some Linux Platform. For Debian/Ubuntu, to install setuptools and pip,

    .. code::

        sudo apt-get install python3-setuptools python3-pip

    If that's a self-compiled Python, try

    .. code::

        python3 -m ensurepip

    For older Python versions, download `get-pip.py <get-pip>`_ and run it.

    .. code::

        python get-pip.py


.. _get-pip: https://bootstrap.pypa.io/get-pip.py

Dependencies
------------

- pathlib_ (for Python 3.3 and below)
- PyYAML_
- docopt_
- Jinja2_

.. _pathlib: https://pypi.python.org/pypi/pathlib
.. _PyYAML: http://pyyaml.org/
.. _docopt: https://github.com/docopt/docopt
.. _Jinja2: http://jinja.pocoo.org/docs/

If one wants to have colorful logging messages, extra packages are required:

- colorlog_
- (or colorlog[windows] on Windows)

.. _colorlog: https://github.com/borntyping/python-colorlog

Install latest stable version
-----------------------------

.. code:: bash

    pip install ngcloud

To get colorful logging message dependencies as well, use

.. code:: bash

    pip install ngcloud[color]


Build from source
-----------------

NGCloud use Gulp.js_, CoffeeScript_, and Stylus_ to build report templates' CSS and JS
with building automation. All frontend dependencies are independently mangaed by npm_.

To build from source, Node.js_ and npm_ are required.
Check their homepage for their installation.

.. code-block:: bash

    git clone https://github.com/BioCloud-TW/ngcloud.git
    cd template_dev
    npm install -g gulp
    npm install

    cd ..  # back to ngcloud source root
    python setup.py install

.. _node.js: http://nodejs.org/
.. _npm: https://www.npmjs.org
.. _gulp.js: http://gulpjs.com/
.. _coffeescript: http://coffeescript.org/
.. _stylus: http://learnboost.github.io/stylus/


Run test
========

Require nose_

.. code:: bash

    nosetest ngcloud

.. _nose: https://nose.readthedocs.org/



Build this doc
==============

You need to installed NGCloud before building the doc. Extra dependencies are

- Sphinx_
- numpydoc_
- sphinx_rtd_theme_

NGCloud source is needed. To install them,

.. code:: bash

    cd docs
    pip install -r requirements.txt
    make html

Documentation will be under ``docs/_build/html/index.html``

For PDF requires XeLaTeX_,

.. code:: bash

    make xelatex

.. _Sphinx: http://sphinx-doc.org
.. _numpydoc: https://github.com/numpy/numpydoc
.. _sphinx_rtd_theme: https://github.com/snide/sphinx_rtd_theme
.. _xelatex: http://www.xelatex.org
