Quick Start
===========


.. _ngreport:

Using ``ngreport``
------------------

High level NGCloud result parser can be accessed by both ways,

.. code-block:: bash

    $ ngreport
    # Usage:
    #     ngreport [-p <pipeline>] <job_dir> [<out_dir>] [-v ...]
    #     ngreport [-p <pipeline>] <job_dir> [-o <out_dir>] [-v ...]
    #     ngreport -h | --help
    #     ngreport --version

    $ python -m ngcloud.report
    # Usage:
    # ... (they access same function)



.. seealso::

    To use the parser inside a Python program, call the function
    :py:func:`ngcloud.report.generate` directly.

