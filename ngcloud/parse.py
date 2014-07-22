#! /usr/bin/env python3.4
# flake8: noqa

from pathlib import Path
from docopt import docopt
import ngcloud as ng

_SCRIPT_DOC = """NGCloud NGS result parser for different pipelines.

Usage:
    ngparse [-p <pipeline>] <job_dir> [<out_dir>] [-v ...]
    ngparse [-p <pipeline>] <job_dir> [-o <out_dir>] [-v ...]
    ngparse -h | --help
    ngparse --version

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

def main():
    args = docopt(_SCRIPT_DOC, version=ng.__version__)
    print(args)

    pipe_type = args['--pipe']
    if pipe_type not in ng.AVAIL_PIPES:
        raise ValueError(
            "Unknown pipeline type: {}".format(pipe_type)
        )

    job_dir = Path(
        args['<job_dir>']
    )
    if not job_dir.exists():
        raise FileNotFoundError(
            'Job info folder: {} does not exist!'.format(job_dir)
        )
    if not job_dir.is_dir():
        raise NotADirectoryError('Expect job info to be dir: {}'.format(job_dir))

    out_dir = Path(
        args['<out_dir>'] if args['<out_dir>'] else args['--outdir']
    )
    verbosity = args['--verbose']

    print(out_dir)

if __name__ == '__main__':
    main()
