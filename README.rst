*******
NGCloud
*******

Documentation: http://ngcloud.readthedocs.org/

Requires Python 3.3+


Installation
============

For Python 3.3 and below, pathlib_ is required prior to the installation.
See `doc <http://ngcloud.readthedocs.org/en/latest/install.html>`_
for more information.

Through *pip*. For latest stable release,

::

    pip install ngcloud


To build from source, Node.js_ and npm_ are required to set up the frontend
development environment to rebuild report templates' CSS/JS.

.. code-block:: bash

    git clone https://github.com/BioCloud-TW/ngcloud.git
    cd template_dev
    npm install

    cd ..  # back to ngcloud source root
    python setup.py install

.. _pathlib: https://pypi.python.org/pypi/pathlib
.. _node.js: http://nodejs.org/
.. _npm: https://www.npmjs.org
