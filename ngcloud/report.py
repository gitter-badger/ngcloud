#! /usr/bin/env python3.4
from pathlib import Path
from docopt import docopt
import ngcloud as ng
from ngcloud.pipe import tuxedo

AVAIL_PIPES = {
    'tuxedo': tuxedo.TuxedoReader
    # FIXME: try to make ng.pipe.tuxedo.TuxedoReader valid import path
}

_SCRIPT_DOC = """\
NGCloud report generator for differenct NGS analysis pipelines.

Usage:
    ngreport [-p <pipeline>] <job_dir> [<out_dir>] [-v ...]
    ngreport [-p <pipeline>] <job_dir> [-o <out_dir>] [-v ...]
    ngreport -h | --help
    ngreport --version

Options:
    -h --help           Show this message.
    -V --version        Show version
    -v --verbose        Increase verbosity (noiser when more -v)
    -p <pipeline>, --pipe=<pipeline>
                        Name of the pipeline [default: tuxedo]
    <job_dir>           Path to the organized job folder [default: .]
    -o <out_dir>, --outdir=<out_dir>, <out_dir>
                        Path to the report output [default: ./output]

"""

_CAVEAT_MSG = '''\
New output result is under {!s}.

The folder can be downloaded and viewed locally.
Quick remainder for serving current folder through http:

    $ python3 -m http.server
    # Serving HTTP on 0.0.0.0 port 8000 ...
'''

class Report:
    pass

def generate(pipe_type_cls, job_dir, out_dir, verbosity=0):
    """Generate a NGCloud report.

    For :ref:`normal usage <ngreport>`, one can use :command:`ngreport` command
    instead of calling this Python function directly.

    Parameters
    ----------
    pipe_type_cls: class
        Python class to generate the report of certain pipeline.
    job_dir: path-like object
    out_dir: path-like object
    verbosity: int
        How noisy the log will be

    Notes
    -----
    To extend NGCloud with your custom pipeline,
    inherit :py:class:`Report` and call this function manually.

    """
    job_dir = Path(job_dir)
    out_dir = Path(out_dir)

    # validate job_dir
    if not job_dir.exists():
        raise FileNotFoundError(    # noqa
            'Job info folder: {} does not exist!'.format(job_dir)
        )
    if not job_dir.is_dir():
        raise NotADirectoryError(   # noqa
            'Expect job info to be dir: {}'.format(job_dir)
        )


def main():
    args = docopt(_SCRIPT_DOC, version=ng.__version__)
    print(args)

    pipe_type = args['--pipe']
    # validate pipe_type
    if pipe_type not in AVAIL_PIPES:
        raise ValueError(
            "Unknown pipeline type: {}".format(pipe_type)
        )
    pipe_type_cls = AVAIL_PIPES[pipe_type]

    job_dir = Path(args['<job_dir>'])
    out_dir = Path(
        args['<out_dir>'] if args['<out_dir>'] else args['--outdir']
    )
    verbosity = args['--verbose']

    generate(pipe_type_cls, job_dir, out_dir, verbosity)

if __name__ == '__main__':
    main()
