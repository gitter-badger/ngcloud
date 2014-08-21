.. _prepare-own-result:

***********************************
Prepare Your NGS Result for NGCloud
***********************************


Organize the result folder
==========================

A standard result folder is like::

    job_tuxedo_minimal
    ├── 1_fastqc
    │   ├── output
    │   └── overall
    ├── 2_tophat
    │   ├── output
    │   └── run.log
    │   (skip other stages) ...
    └── job_info.yaml

Each subfolder corresponds to a stage, the prefix number (Ex ``1_``, ``2_``) has no meaning but merely enhances readability. Folder name excluding prefix should match :py:attr:`Stage.result_foldername <ngcloud.report.Stage.result_foldername>` specified by the stage.

Specify the ``job_info.yaml``
=============================

File job_info.yaml follows YAML_ syntax, which stores how the NGS analysis pipeline is performed and the sample information. YAML is a human readable format to store natural data structure. The following is the YAML content of our minimal example:

.. literalinclude:: ../../examples/job_tuxedo_minimal/job_info.yaml
    :language: yaml
    :linenos:

.. _YAML: http://en.wikipedia.org/wiki/YAML

It specifies:

- **job_type**: pipeline that the NGS result is performed
- **job_id**: an auto-generated job ID. If that's a custom result, type in a summary name for this job.
- **sample_list**: list of samples used in this job and their properties.

Sample list
-----------

.. warning:: Mind the format and indentation how a sample_list is specified.

.. code:: yaml

    sample_list:
        - <sample_name>:
            <property_A>: <value>
        - <sample_name>:
            <property_A>: <value>
            <property_C>: <value>

A general sample_list structure is like the above example. Some properties may be shared across samples such as **pair_end**, while some may be unique for certain samples such as **stranded**. Only the specified properties will be defined.

Pair-end
""""""""
For now, **pair_end**, the pair-end type of a sample, is *highly recommended* to be specified for all samples.
If a sample is single-ended sequenced, set the value to ``False``:

.. code:: yaml

    - single_end_sample:
        pair_end: False

While for a pair-end sample, one needs to create separate records for both ends:

.. code:: yaml

    - a_pairend_sample:
        pair_end: R1
    - a_pairend_sample:
        pair_end: R2

Of course, if only one end of a pair-end sample is used, only one record needs to be created.

To find out what properties can be set to a sample, see :py:class:`ngcloud.info.Sample` for more info.

.. note::

    Currently, there is nothing important but sample list to be specify in ``job_info.yaml``.
    While as report templates evolve and use more arguments and information, there will be more requirements about the format.
