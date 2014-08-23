.. _prepare-own-result:

***********************************
Prepare Your NGS Result for NGCloud
***********************************

To make NGCloud recongize your NGS results, the result folder structure should follow the results specify by NGCloud and the corresponding pipeline.

Here we first introduce some general rules, and you could get the whole picture and the find out details in each pipeline, say :py:mod:`ngcloud.pipe.tuxedo` for Tuxedo.


Organize the result folder
==========================

A standard result folder looks like the following::

    job_tuxedo_minimal/
    ├── 1_fastqc/
    │   ├── SRR1027176_R1/
    │   ├── SRR1027176_R2/
    │   ├── SRR1027183_R1/
    │   └── SRR1027183_R2/
    ├── 2_tophat/
    │   ├── SRR1027176/
    │   └── SRR1027183/
    │   (skip other stages) ...
    └── job_info.yaml

This example is taken from the bundled example under :file:`examples/job_tuxedo_minimal`. Later we will refer this as **result's root**.

Each subfolder corresponds to a stage of the pipeline. Whether the prefix number (Ex ``1_``, ``2_``) exists does not matter but merely enhances readability. Folder name excluding prefix should match :py:attr:`Stage.result_foldername <ngcloud.report.Stage.result_foldername>` specified by each stage. Later we will refer this folder for each stages as **stage's root**.

How the results is orgnazied below stage's root depends on how the stage work. A stage is likely producing results with forms:

- Only *one* set of result is created, no matter how many samples it takes (**joint mode**)
- A set of result is created for *every* input sample (**per-sample mode**)
- Multiple sets of result are created, but a set if for a *group* of samples (**per-group mode**)

For the first case (**joint mode**), since there is only a set of result, the result files usually directly lies right below the stage's root. For example, Cuffdiff produces a set of comparison for any two conditions.

For the second case (**per-sample mode**), there are sets for each result, so a subfolder is created and named by the *sample's full name*. We will take more on sample's naming later. For example, FastQC produces quality report for all samples. As one can see, pair-end samples (e.g., both SRR1027176 and SRR1027183) will have two sets of results.

For the third case (**pre-group mode**), there are sets for each group of samples. There are many grouping for samples so it depends on what the stage uses. For example, Tophat will group pair-end samples because it takes pair-end information during alignment. And pair-end grouping is the most common grouping scheme. The subfolders under stage's root shuld be named by sample name.


Specify the job_info.yaml
=========================

File :file:`job_info.yaml` follows YAML_ syntax, which stores how the NGS analysis pipeline is performed and the sample information. YAML is a human readable format to store natural data structure. The following is job_info.yaml of our minimal result:

.. literalinclude:: ../../examples/job_tuxedo_minimal/job_info.yaml
    :language: yaml
    :linenos:

.. _YAML: http://en.wikipedia.org/wiki/YAML

Generally it specifies:

- **job_type**: pipeline that the NGS result is performed
- **job_id**: an auto-generated job ID. If that's a custom result, type in a summary name for this job.
- **sample_list**: list of samples used in this job and their properties.


Sample list
-----------

.. code:: yaml

    sample_list:
        - <sample_name>:
            <property_A>: <value>
        - <sample_name>:
            <property_A>: <value>
            <property_C>: <value>

A general sample_list structure is like the above example. Some properties may be shared across samples such as **pair_end**, while some may be unique for certain samples such as **stranded**. Only the specified properties will be defined.

.. warning:: Mind the format and indentation how a sample_list is specified.

Pair-end
""""""""
**pair_end** denotes the pair-end type of a sample, and is *highly recommended* to be specified for all samples.
If a sample is single-ended sequenced, set the value to ``False``:

.. code:: yaml

    - single_end_sample:
        pair_end: False

Then in the example, the **sample name** and **full sample name** will both be ``single_end_sample``.

While for a pair-end sample, one needs to create separate records for both ends:

.. code:: yaml

    - a_pairend_sample:
        pair_end: R1
    - a_pairend_sample:
        pair_end: R2

Of course, if only one end of a pair-end sample is used, only one record needs to be created.
In this case, **sample name** and **full sample name** for the first strand are ``a_pairend_sample_R1`` and ``a_pairend_sample`` respectively.

To find out what properties can be set to a sample, see :py:class:`ngcloud.info.Sample` for more info.

.. note::

    Currently, there is nothing important but sample list to be specify in ``job_info.yaml``.
    While as report templates evolve and use more arguments and information, there will be more requirements about the format.

By knowing the format of result folder structure and job_info.yaml, you can proceed to the next section to build your own pipeline from ground up.
