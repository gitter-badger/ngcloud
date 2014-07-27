import shutil
import os.path as op
from pathlib import Path
import ngcloud as ng

logger = ng._create_logger(__name__)

def open(path_like, *args, **kwargs):
    """Custom open() that accepts :py:class:`pathlib.Path` object.

    All the parameters will be passed to original :py:func:`python:open`.

    Examples
    --------

        >>> with open(Path('say'), 'w') as f:
        ...     f.write('hi')

    """
    logger.debug(
        "File {0!s} is open by custom open() function "
        "with extra arguments: args={1} kwargs={2}"
        .format(path_like, args, kwargs)
    )
    if isinstance(path_like, Path):
        return path_like.open(*args, **kwargs)
    else:
        return open(path_like, *args, **kwargs)


def abspath(path_like):
    """Custom abspath() that accepts both str and Path object.

    Internally it calls :py:func:`os.path.abspath`
    """
    if isinstance(path_like, Path):
        return op.abspath(path_like.as_posix())
    else:
        return op.abspath(path_like)


def expanduser(path_like):
    """Custom expanduser() that accepts both str and Path object.

    Internally it calls :py:func:`os.path.expanduser`
    """
    if isinstance(path_like, Path):
        return op.expanduser(path_like.as_posix())
    else:
        return op.expanduser(path_like)


def copy(src_path_like, dst_path_like, metadata=False, **kwargs):
    """pathlib support for path-like objects.

    Internally use either :py:func:`shutil.copy` or :py:func:`shutil.copy2`
    based on `metadata` value.
    """
    if metadata:
        _copy_cmd = shutil.copy2  # copy2 perserves metadata
    else:
        _copy_cmd = shutil.copy

    # TODO: use system command for large file
    _copy_cmd(
        strify_path(src_path_like), strify_path(dst_path_like), **kwargs
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

    Returns
    -------
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
    # if input is str
    if isinstance(file_patterns, str):
        found_file_list = list(Path(path_like).glob(file_patterns))
        logger.info(
            "{2} file matching single pattern {1} under {0!s}"
            .format(path_like, file_patterns, len(found_file_list))
        )

    # if input is iterable
    try:
        discovered_file_list = []
        for pattern in file_patterns:
            if not isinstance(pattern, str):
                raise TypeError(
                    "File pattern should be str, not {}".format(file_patterns)
                )
            file_list = list(Path(path_like).glob(pattern))
            logger.debug(
                "... {} file found by {}"
                .format(len(file_list), pattern)
            )
            discovered_file_list.extend(file_list)
        logger.info(
            "{2} file matching patterns {1!r} under {0!s}"
            .format(path_like, file_patterns, len(discovered_file_list))
        )
        return discovered_file_list
    except TypeError as te:
        raise ValueError(
            "Unexpect file_patterns: {}, "
            "should be str or iterable of str elements."
            .format(file_patterns)
        ) from te


def strify_path(path_like):
    """Normalized path-like object to POSIX style str.

    Examples
    --------

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
        raise TypeError(
            "Unknown type {} for path-like object".format(type(path_like))
        )


def is_pathlike(path_like):
    """Helper function to determine is pathlike object."""
    if isinstance(path_like, Path) or isinstance(path_like, str):
        return True
    else:
        return False


def _val_bool_or_none(arg, name):
    """Check if argument is of True, False, or None.

    Otherwise :py:exc:`ValueError` is raised.

    Raises
    ------
    ValueError

    """
    if not isinstance(arg, bool) and arg is not None:
        raise ValueError(
            "Expect {0} to be True, False or None".format(name)
        )


