.. _custom_pipe_groundup:

Custom a Pipeline from Ground up
================================

.. contents:: Table of Contents
    :depth: 2
    :backlinks: entry

The whole process can be considered as three main steps:

- Design Jinja2 templates to determine how your report looks like in a web browser
- Translated all NGS tools that its output needs to display into a new class that inherits :py:class:`ngcloud.report.Stage`.
- Create a new class inherits :py:class:`ngcloud.report.Report` to collect all your needed stages.

You will create your first pipe after this section. Here we are going to create a new pipeline with two stages. See :file:`{ngcloud_src}/examples/my_first_pipe` for the final result.


Goal
----

In this pipeline, there will be two stages:

- **index**: shows hello message and the job ID
- **mystage**: lists sample in use and show the overall alignment rate

Overall alignment rate is logged inside a output file :file:`summary.txt`, represented as some NGS results we'd like to extract and shown them in our reports.


General folder structure
------------------------

We organize all the files needed in our recommended folder structure::

    my_first_pipe/
    ├── report/
    │   ├── static/
    │   └── templates/
    │       ├── base.html
    │       ├── index.html
    │       └── mystage.html
    ├── job_demo_result/
    │   ├── my_stage/
    │   │   └── summary.txt
    │   └── job_info.yaml
    └── mypipe.py

**mypipe.py** is where Python scripts and report logics are stored. The filename *mypipe* needs to match the Python module naming rule so later we could import it.

**job_demo_result** we fake a NGS result, assuming it follows the `mypipe` pipeline.

**report/** folder keeps all the template-related files.

Insides report folder, all templates go under **templates/**, if you have some experience with web's template engine you will find it familiar. In fact, Jinja2_ is indeed a awesome template engine that used by many Python-powered websites.

Other files such as CSS or JS that decorate the reports go under **static/**. These are stuff that we used in the report but we aren't likely to modify it. Therefore they are called as static files.

We will explain each part in the following sections.

.. _Jinja2: http://jinja2.pocoo.org/


Organize the NGS result
-----------------------

Since we only have a stage `mystage` that holds output files, the result folder is rather simple.
We set the root folder as **job_demo_result**. The folder looks like this::

    my_first_pipe/job_demo_result/
    ├── my_stage/
    │   └── summary.txt
    └── job_info.yaml

**summary.txt** holds the NGS output by my_stage, and is where we need to extract the overall alignment rate from.

.. literalinclude:: ../../examples/my_first_pipe/job_demo_result/my_stage/summary.txt

**job_info.yaml** stores how the result is performed. Currently only the sample info is stored.

.. literalinclude:: ../../examples/my_first_pipe/job_demo_result/job_info.yaml
    :language: yaml

Two samples are used, ngs_A is pair-end while ngs_B is single-ended. ID and job type are also stated.


Write stage template
--------------------

First we look back on what we want for our first pipeline:

- An index page (**index.html**) shows hello message
- A stage page (**mystage.html**) prints some value from our fake NGS results.

Before we really touch these two templates, first we create a base template to store the common part. You will soon see the benefit maintaining such templates. We called it **base.html**.

.. literalinclude:: ../../examples/my_first_pipe/report/templates/base.html
    :language: jinja
    :emphasize-lines: 6,9

So base.html is just a mini working HTML5 file. By declaring blocks *title* and *content*, later base.html can be inherited by stage templates and their content can be override.

**index.html** will be built upon base.html.

.. literalinclude:: ../../examples/my_first_pipe/report/templates/index.html
    :language: jinja

First we extend the base templates and overwrite the *title* block. As for *content* block, we show a hello message, and we left a variable ``{{ job_info.id }}`` to represent the job id. When a report is being rendered, **job_info**, a :py:class:`~ngcloud.info.JobInfo` object, will be passed so we could use its value.

In **mystage.html** we will use this variable passing mechanism more extensively.

Since job_info contains the sample list, we would like to print them out. Also, we wish to display the overall alignment rate.

Here is how to get it done. First we make the sample list,

.. literalinclude:: ../../examples/my_first_pipe/report/templates/mystage.html
    :language: jinja
    :lines: 5-11,15

By using `Jinja2's for-loop <jinja-for>`_ control structure, we could extract the sample list from job_info, in each is a :py:class:`~ngcloud.info.Sample` object. So we use sample's full name to display our sample list.

As for showing the overall alignment rate, since it is not some default information, we need to create our own variables and passed it into templates explicitly.

By default, a dict-like variable **result_info** will always be passed, and we could modify the key-value pairs it holds during :py:meth:`ngcloud.report.Stage.parse`. We name the key representing the overall alignment rate as **mapped_rate**. Therefore in template we could

.. literalinclude:: ../../examples/my_first_pipe/report/templates/mystage.html
    :language: jinja
    :lines: 5, 13-15

Then we join these two piece together in a same *content* block. And we finished our first pipeline template design.

.. seealso:: :py:meth:`ngcloud.report.Stage.render` talks more about the mechanism passing **job_info** and **result_info**.

.. _jinja-for: http://jinja.pocoo.org/docs/templates/#for

Write the report logics
-----------------------
