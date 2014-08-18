.. _extend_builtin_pipe:

Extend Builtin Pipeline
=======================

.. contents:: Table of Contents
    :depth: 2
    :backlinks: entry

We prepare a example under :file:`{ngcloud_src}/examples/gatk/` to show how to extend a builtin pipeline to display GATK pipeline results.

There are many reason to extend a exited pipeline:

- To use the well-designed report layout
- To Build a new pipeline by reusing existed parts
- To extend certain pipeline's functionality

In the following, we will introduce the difference from :ref:`custom_pipe_groundup` and explore more NGCloud's APIs in detail.


Reues builtin templates
-----------------------

By extending existed pipeline, especially builtin ones, there are mainly two things to remember:

- For each stage, specify path to builtin templates in **template_find_paths** by :py:func:`ngcloud.pipe.get_shared_template_root`
- For the pipeline (or the Report subclass), specify path to builtin static files in **static_roots** by :py:func:`ngcloud.pipe.get_shared_static_root`

Using :func:`!get_shared_template_root` and :func:`!get_shared_static_root` makes sure you can always find the correct path to builtin files no matter how you install NGCloud.

Here is a simple example to show how to re-use builtin templates.

.. code-block:: python3
    :emphasize-lines: 10, 20

    from pathlib import Path
    from ngcloud.report import Stage, Report
    from ngcloud.pipe import (
        get_shared_template_root, get_shared_static_root
    )

    class MyBaseStage(Stage):
        template_find_paths = [
            Path('myreport', 'templates'),
            get_shared_template_root(),
        ]

    class MySomeStage(MyBaseStage):
        template_entraces = 'some_stage.html'

    class MyReport(Report):
        stage_classnames = [MySomeStage]
        static_roots = [
            Path('myreport', 'templates'),
            get_shared_static_root(),
        ]

Highlighted lines are modifications from :ref:`custom_pipe_groundup`.

For **template_fine_paths** of Stage, you should put your own paths *before* builtin to make sure your customs templates are always searched first.

For **static_roots** of Report, the order of static file paths usually don't matter. But if you want to overwrite some built-in static files, you should put your custom static files *after* builtin static paths.

.. note::

    Notice the hieracrhical order of template find paths.

    Templates are first looked up in the path coming first. If some templates are not found, the template engine will look up in the next find path.
    Finally a :py:exc:`jinja2.TemplateNotFound` is thrown after all find paths being searched in vain.

    If the render results are unexpected, it may be the filename conflicts between builtin and custom tempaltes.
    A common situation is unexpectedly overwrite some templates that are needed for builtin report parts.

.. note::

    If a static file is overwritten, a warning will be given during the generating process.
    If it is not the desired behavior, look at the conflict filename in log and rename it to prevent overwriting.

    Usually you will want to overwrite builtin static files when you are developing built-in pipelines in :file:`template_dev`.
    Those topics are coverd at :ref:`more_template_dev`.


Reuse builtin stages
--------------------

Reusing some stages from other pipelines is easy. Take quality control (QC) stage as example, almost every pipeline requires QC. Therefore using builtin QC can ease lots of builing-the-wheel efforts.

Currently the QCStage is defined inside :py:mod:`ngcloud.pipe.tuxedo`. The stage also ships with the stage-specific static files copying logics, so one don't need to mind how to collect the figures to show in report.

To make sure full QCStage functionality works, one may first include the stage directly,

.. code-block:: python3
    :emphasize-lines: 4

    from ngcloud.pipe import tuxedo

    class MyReport(Report):
        stage_classnames = [tuxedo.QCStage, MySomeStage]
        # ...

But it will generate some problems:

    1. Path for tuxedo's template find paths are not specified.
    2. Display of the stage pipes gets wrong info in report.
    3. Tuxedo's static files are not included.

All will fail the qcstage to work properly.

To correctly display the our custom stage pipes, which is originally specified by :file:`_stage_pipe.html` template, we could defined a new :file:`_stage_pipe.html` in our template find path so it will override the builtin one.

So the new code looks like this,

.. code-block:: python3
    :emphasize-lines: 4-

    from ngcloud.pipe import tuxedo

    class MyQCStage(tuxedo.QCStage):
        template_find_paths = (
            MyBaseStage.template_find_paths[:1] +   # include only custom template find path
            tuxedo.QCStage.template_find_paths
        )

We *inherit* the QCStage class, and carefully treat the template find paths here. Only first path in MyBaseStage is included so the builtin shared templates will not come before tuxedo-specific templates.

Also the path to Tuxedo's static files should be specified in our Report as well. All builtin pipelines of course include builtin shared static files, we could modify the **static_roots** into:

.. code-block:: python3
    :emphasize-lines: 2-3

    class MyReport(Report):
        static_roots = tuxedo.TuxedoReport.static_roots[:]  # must copy list
        static_roots.append(Path('myreport', 'static'))

.. note::

    Make sure to use list copying instead of direct assign. Here is how the direct assigning works,

        >>> a = ['path1', 'path2']
        >>> b = a
        >>> b.append('path3')
        >>> a
        ['path1', 'path2', 'path3']

    If one set::

        static_roots = tuxedo.TuxedoReport.static_roots
        static_roots.append(...)

    Then static_roots of Tuxedo pipeline will be modified also. Use copying to protect original list,

        >>> b = a[:]
        >>> b.append('path3')
        >>> a
        ['path1', 'path2']


Override builtin template behaviour
-----------------------------------

.. warning:: Do it with care. Builtin templates are less documented.

You could always change the builtin template's behavior by overriding methods in subclass. But generally you would like to preserve most of their functionality.

If we want to extend the :py:func:`Stage.parse <ngcloud.report.Stage.parse>` behavior of QCStage, here's the Pythonic trick:

.. code-block:: python3
    :emphasize-lines: 5

    class MyQCStage(tuxedo.QCStage):
        # template_find_paths = ...

        def parse(self):
            super(tuxedo.QCStage, self).parse()
            # write the custom logics here
            self.result_info.update({
                'my_desired_property', None
            })

Then when a report is being generated, MyQCStage's parse() will be called, in which the original QCStage's parse() is first performed through :py:func:`super`, followed by our custom logics.

By making this trick, you could always insure that all original logics are preserved.
