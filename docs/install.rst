Installation
============

Require Python 3.4+, setuptools, and pip. Other Python versions are not tested.


.. note:: Python 3.4+ should come along with setuptools and pip, but that's not always the case on some Linux Platform. For Debian/Ubuntu, to install setuptools and pip,

    .. code::

        sudo apt-get install python3-setuptools python3-pip

    If that's a self-compiled Python, try

    .. code::

        python3 -m ensurepip

    For older versions, download `get-pip.py <get-pip>`_ and run it.

    .. code::

        python get-pip.py


.. _get-pip: https://bootstrap.pypa.io/get-pip.py

Dependencies
------------

- PyYAML_
- docopt_
- Jinja2_

.. _PyYAML: http://pyyaml.org/
.. _docopt: https://github.com/docopt/docopt
.. _Jinja2: http://jinja.pocoo.org/docs/


Install from PyPI
-----------------

*Not yet supported*


Install from source
-------------------

Through one-liner,

.. code:: bash

    pip install git+https://github.com/ccwang002/ngcloud.git@master

or clone the source then run

.. code:: bash

    python setup.py install


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

.. _Sphinx: http://sphinx-doc.org
.. _numpydoc: https://github.com/numpy/numpydoc
.. _sphinx_rtd_theme: https://github.com/snide/sphinx_rtd_theme
