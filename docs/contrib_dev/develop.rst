**********
Developing
**********

Installation
============
One is encouraged to develop under a virtual environment.

To immediately reflect code change, install NGCloud in development mode:

.. code-block:: bash

    python setup.py develop
    # or
    pip install -e .[all]

Extra dependencies are required to enable syntax checking::

    pip install -r requirements_dev.txt


Automated building
==================

When developing templates or writing docs, one may constantly needs to run :command:`make html` or :command:`ngreport` to see the changed outputs.
But that is sometimes demanding so here is some trick for automated building when sources change.

Requires watchdog_. Take building docs as example, under :file:`docs` run:

.. code-block:: bash

    watchmedo shell-command \
        --interval 10 --wait --drop \
        --recursive --paterns="*.rst" \
        --command='make html' .

Then watchdog will monitor the doc folder and run :command:`make html` when any rst file changes.

.. _watchdog: https://github.com/gorakhargosh/watchdog


Deploy to PyPI
==============

.. code-block:: bash

    python setup.py egg_info -RDb '' sdist wheel --universal
    python setup.py egg_info -RDb '' register
    twine upload dist/*

