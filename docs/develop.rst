**********
Developing
**********

Installation
============

One is encouraged to develop inside a virtual environment.

Make sure the the frontend development environment is properly set.

.. code-block:: bash

    cd template_dev
    npm install -g gulp
    npm install

To immediately reflect code change, install NGCloud under develop mode:

.. code-block:: bash

    python setup.py develop
    # or
    pip install -e .[all]

Extra dependencies are required to enable syntax checking::

    pip install -r requirements_dev.txt


Building frontend CSS/JS
========================

Javascript and CSS for builtin templates are built from CoffeeScript_ and Stylus_ sources under :file:`template_dev/src`, which provide succinct and maintainable syntax.

From a frontend developer's point of view, their building process has been well-defined in **gulpfile.coffee** and been managed by Gulp.js_,

.. code-block:: bash

    # under template_dev
    gulp coffee     # generate js files under ./js
    gulp stylus     # generate css files under ./css
    gulp            # generate both js and css

    gulp release    # generate both js and css under ngcloud/pipe/report/static

    gulp clean

From a Python developer's point of view, learning the frontend knowledge requires great effort. So these details have been hidden inside **setup.py**.

Every time source are updated and new CSS/JS build is required, run

.. code-block:: bash

    python setup.py build_frontend

This will have the same effect as **gulp release**.

.. warning::

    Never modified generated CSS/JS *directly*.
    They will be overwritten without warning everytime building being triggered

.. _node.js: http://nodejs.org/
.. _npm: https://www.npmjs.org
.. _gulp.js: http://gulpjs.com/
.. _coffeescript: http://coffeescript.org/
.. _stylus: http://learnboost.github.io/stylus/

Automated building
==================

When developing templates or writing docs, one may constantly needs to run :command:`make html` or :command:`ngreport` to see the changed outputs.
But that is sometimes demanding so here is some trick for automated building when sources change.

Requires watchdog_. Take building docs as example, under :file:`docs` run:

.. code-block:: bash

    watchmedo shell-command \
        --interval 3 --wait --drop \
        --recursive --patterns="*.rst" \
        --command='make html' .

Then watchdog will monitor the doc folder and run :command:`make html` when any rst file changes.

.. _watchdog: https://github.com/gorakhargosh/watchdog

Frontend CSS/JS
---------------

There are plenty of ways to watch their source change. Under :file:`template_dev` run:

.. code-block:: bash

    gulp watch  # it ingores events of new file created
    make        # below it calls the watchmedo then calls gulp


Deploy to PyPI
==============

Original version:

.. code-block:: bash

    python setup.py egg_info -RDb '' build_frontend sdist --formats="gztar,zip" bdist_wheel --universal
    python setup.py egg_info -RDb '' register
    twine upload dist/*

Simplified version:

.. code-block:: bash

    python setup.py release sdist bdist_wheel   # check output
    python setup.py release register
    twine upload dist/*
