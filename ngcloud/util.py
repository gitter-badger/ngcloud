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


def strify_path(path_like):
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


