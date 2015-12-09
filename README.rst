*******
NGCloud
*******

Documentation: http://ngcloud.readthedocs.org/

Requires Python 3.3+


Installation
============

Through *pip*. For latest stable release,

::

    pip install ngcloud


Build from source
-----------------

Node.js_ and npm_ are required to set up the frontend
development environment.

.. code-block:: bash

    git clone https://github.com/BioCloud-TW/ngcloud.git
    cd template_dev
    npm install
    npm install -g gulp

    cd ..  # back to ngcloud source root
    python setup.py install

.. _pathlib: https://pypi.python.org/pypi/pathlib
.. _node.js: http://nodejs.org/
.. _npm: https://www.npmjs.org


.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/BioCloud-TW/ngcloud
   :target: https://gitter.im/BioCloud-TW/ngcloud?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge