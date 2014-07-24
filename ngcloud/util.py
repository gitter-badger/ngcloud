from pathlib import Path
import os.path as op
import shutil

def open(path_like, *args, **kwargs):
    """Custom open() that accepts :py:class:`pathlib.Path` object.

    All the parameters will be passed to original :py:func:`python:open`.


    Examples
    --------

        >>> with open(Path(), 'w') as f:
        ...     f.write('hi')

    """
    if isinstance(path_like, Path):
        return path_like.open(*args, **kwargs)
    else:
        return open(path_like, *args, **kwargs)


def abspath(path_like):
    """Custom abspath() that accepts both str and :py:class:`pathlib.Path`."""

    if isinstance(path_like, Path):
        return op.abspath(path_like.as_posix())
    else:
        return op.abspath(path_like)


def expanduser(path_like):
    if isinstance(path_like, Path):
        return op.expanduser(path_like.as_posix())
    else:
        return op.expanduser(path_like)


def copy(src_path_like, dst_path_like, metadata=False, **kwargs):
    """pathlib support for path-like objects."""

    if metadata:
        _copy_cmd = shutil.copy2  # copy2 perserves metadata
    else:
        _copy_cmd = shutil.copy

    # TODO: use system command for large file
    _copy_cmd(
        strify_path(src_path_like), strify_path(dst_path_like),
        **kwargs
    )


def discover_file_by_patterns(path_like, file_patterns="*"):
    """Discover files under certain path based on given patterns.

    Support both ``**`` and ``*`` globbing syntax.
    Call :py:func:`pathlib.Path.glob` internally.

    Parameters
    ----------
    path_like : path-like object
    file_patterns : str or iterable
        glob-style file pattern

    Return
    ------
    List of :py:class:`pathlib.Path` object.

    Examples
    --------

        >>> discover_file_by_patterns("report", "**/_*.html")
        [PosixPath('report/templates/_nav.html'),
         PosixPath('report/templates/_footer.html'),
         PosixPath('report/templates/_stage_pipe.html')]
        >>> discover_file_by_patterns("report", ["**/_*.html", "**/*.js"])
        [PosixPath('report/templates/_nav.html'),
         PosixPath('report/templates/_footer.html'),
         PosixPath('report/templates/_stage_pipe.html'),
         PosixPath('report/static/vendor/bootstrap-3.1.1/js/bootstrap.min.js'),
         PosixPath('report/static/vendor/bootstrap-3.1.1/js/bootstrap.js')]

    """
    try:
        discovered_file_list = []
        for pattern in file_patterns:
            discovered_file_list.extend(path_like.glob(pattern))
        return discovered_file_list
    except TypeError:
        if isinstance(file_patterns, str):
            return path_like.glob(file_patterns)
        else:
            raise TypeError(
                "Unexpect file_patterns: {},"
                "should be str or iterable of str elements."
                .format(file_patterns)
            )

def strify_path(path_like):
    """Normalized path-like object to POSIX style str.

    Examples
    -------

        >>> strify_path(Path('ngcloud') / 'hi.py'))
        "ngcloud/hi.py"
        >>> strify_path('ngcloud/hi.py')
        "ngcloud/hi.py"

    """
    if isinstance(path_like, Path):
        return path_like.as_posix()
    elif isinstance(path_like, str):
        return path_like
    else:
        raise ValueError(
            "Unknown type {} for path-like object".format(type(path_like))
        )


def _val_bool_or_none(arg, name):
    """Check if argument is of True, False, or None.

    Otherwise :py:exc:`ValueError` is raised.

    Raises
    ------
    ValueError

    """
    if not isinstance(arg, bool) and not arg is None:
        raise ValueError(
            "Expect {0} to be True, False or None".format(name)
        )


