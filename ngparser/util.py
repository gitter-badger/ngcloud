from pathlib import Path
import os.path as op

def open(path_like, *args, **kwargs):
    """Custom open() that accepts pathlib.Path object.

    All the parameters will be passed to original :py:func:`open`.

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
    """Custom abspath() that accepts both str and pathlib.Path."""

    if isinstance(path_like, Path):
        return op.abspath(path_like.as_posix())
    else:
        return op.abspath(path_like)

def expanduser(path_like):
    if isinstance(path_like, Path):
        return op.expanduser(path_like.as_posix())
    else:
        return op.expanduser(path_like)


def _val_bool_or_none(arg, name):
    """Check if argument is of True, False, or None.

    Otherwise ValueError is raised.

    Raises
    ------
    ValueError

    """
    if not isinstance(arg, bool) and not arg is None:
        raise ValueError(
            "Expect {0} to be True, False or None".format(name)
        )


