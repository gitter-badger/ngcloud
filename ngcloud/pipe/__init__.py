from pathlib import Path

_here = Path(__file__).parent

def _get_builtin_template_root():
    return _here / 'report' / 'templates'

def get_shared_static_root():
    """Return path to shared static files of builtin NGCloud report.

    """
    return _here / 'report' / 'static'

def get_shared_template_root():
    """Return path to shared template root of builtin NGCloud report.

    The functions help one to extend current pipeline externally.
    The path returned depends on your installation path,
    but usually is :file:`{ngcloud_package}/pipe/report/templates/shared`

    When extending stage of a pipeline, one can faciliate shared templates
    by supplying this path to
    :py:attr:`~ngcloud.report.Stage.template_find_paths`

    .. code-block:: python3

        class MyStage(Stage):
            template_find_paths = [
                get_shared_template_root(),
                Path('path' / 'to' / 'custom' / templates')
            ]

    Returns
    -------
    :py:class:`~pathlib.Path` object
    """
    return _get_builtin_template_root() / 'shared'
