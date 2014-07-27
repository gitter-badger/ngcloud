import shutil
import os
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


def merged_copytree(src_list, dst):
    dst_p = Path(dst)
    if not dst_p.exists():
        dst_p.mkdir()
    for src in src_list:
        src_p = Path(src)
        for current_root, dirs, files in os.walk(strify_path(src)):
            # logger.debug(
            #     'current_root: {}, dirs: {}, files: {}'
            #     .format(current_root, dirs, files)
            # )
            current_p = Path(current_root)
            rel_to_src_root = current_p.relative_to(src_p)
            dst_current_d = dst_p / rel_to_src_root
            if not dst_current_d.exists():
                logger.debug(
                    "Destination dir: {!s} not existed, created."
                    .format(dst_current_d)
                )
                dst_current_d.mkdir()
            for f in files:
                src_f = current_p / f
                dst_f = dst_current_d / f
                logger.debug('{!s} -> {!s}'.format(src_f, dst_f))
                try:
                    copy(src_f, dst_current_d)
                except FileExistsError as e:
                    logger.warn("Copying error {!r}".format(e))

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


