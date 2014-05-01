*******
NGCloud
*******

Current Status
==============

- work on pipeline Tuxedo(Tophat -> Cufflinks)


Demo Pipelines
==============

All pipeline examples are under ``demo-pipe``.

Watchdog
--------

To monitor a folder change,

.. code-block:: bash

    watchmedo shell-command --recursive \
        --command='python gen_tuxedo_report.py' \
        report # folder under watch
