.. _prepare-own-result:

***********************************
Prepare Your NGS Result for NGCloud
***********************************


Organize the result folder
==========================

A standard result folder is like::

    job_9527_tuxedo
    ├── 1_fastqc
    │   ├── output
    │   └── overall
    ├── 2_tophat_176
    │   ├── output
    │   └── run.log
    ├── 3_tophat_183
    │   ├── output
    │   └── run.log
    │   (skip other stages) ...
    └── job_info.yaml


Specify the ``job_info.yaml``
=============================

``job_info.yaml`` follows YAML_ syntax, which stores how the NGS analysis pipeline is performed and the sample information. YAML_ is a human readable format to store natural data structure.

.. literalinclude:: ../../examples/job_9527_tuxedo_minimal/job_info.yaml
    :language: yaml
    :linenos:

.. _YAML: http://en.wikipedia.org/wiki/YAML


Sample info
-----------


Job info
--------
