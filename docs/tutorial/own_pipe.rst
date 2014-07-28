Make a new NGCloud Pipeline
===========================

.. _custom_pipe_groundup:

Custom a Pipeline from Ground up
--------------------------------

- Design Jinja2 templates to determine how your report looks like in a web browser
- Translated all NGS tools that its output needs to display into a new class that inherits :py:class:`ngcloud.report.Stage`.
- Create a new class inherits :py:class:`ngcloud.report.Report` to collect all your needed stages.


.. _extend_builtin_pipe:

Extend Builtin Pipeline
-----------------------

We have prepared a example under :file:`{ngcloud_src}/examples/gatk/` to show how to extend a builtin pipeline to display GATK pipeline results.
