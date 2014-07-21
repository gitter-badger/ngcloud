Contributing
============

For the full guideline, see ``docs/contrib_dev/contributing.rst``.


Code Style
----------

Follows PEP8_.

NGCloud use use flake8_ as syntax and style checker.


Version Control
---------------

NGCloud use Git for source control, and is hosted on GitHub.

Commit Messages
"""""""""""""""

Refer `this style <git-msg-rule>`_ as our general rules.

Keep each commit *small*.

Git Branching
"""""""""""""

*(Not applied yet but keep it in mind)*

Use the branching model stated in `this post <git-branch>`_:

- ``master``: stable release, only accepts merge from develop
- ``develop``: latest development
- other branches: each for a large feature, removed after being merged into master.

.. _PEP8: http://legacy.python.org/dev/peps/pep-0008/
.. _flake8: http://flake8.readthedocs.org/
.. _git_msg_rule: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
.. _git_branch: http://nvie.com/posts/a-successful-git-branching-model/
