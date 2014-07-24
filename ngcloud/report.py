#! /usr/bin/env python3.4
import importlib
import shutil
from pathlib import Path
import abc
import logging
from docopt import docopt
import jinja2
import ngcloud as ng
from ngcloud.util import strify_path, open
from ngcloud.info import JobInfo

logger = ng._create_logger(__name__)

AVAIL_PIPES = {
    'tuxedo': 'ngcloud.pipe.tuxedo.TuxedoReport'
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


class Stage(metaclass=abc.ABCMeta):
    template_name = ''

    def __init__(self, job_info, report_root):
        self._setup_jinja2()
        self._template = self._env.get_template(
            "%s.html" % self.template_name
        )
        self.job_info = job_info
        self.report_root = report_root

    def _setup_jinja2(self):
        self._report_loader = jinja2.FileSystemLoader(
            self.template_root.as_posix()
        )
        self._env = jinja2.Environment(
            loader=self._report_loader,
            extensions=['jinja2.ext.with_'],
        )
        self._env.globals['static'] = self._template_static_path

    def _template_static_path(self, path):
        return 'static/%s' % path

    def render(self):
        return self._template.render(job_info=self.job_info)

    def copy_static(self):
        """Copy stage-specific static files under report folder."""
        pass


class Report(metaclass=abc.ABCMeta):
    """NGCloud report base class of every pipeline.

    To combind custom pipeline with :command:`ngreport`,
    :py:meth:`__init__` signature must match :py:class:`Report`.
    Setup the custom logics in :py:func:`template_config`

    Attributes
    ----------
    job_info
    out_dir
    report_root
    stage_template_cls : list of class
        List of stage class name in order used in for this pipeline report.
    static_root : Path
        Path to the template static file dir

    Raises
    ------
    TypeError
        When initiate this class directly,
        or subclass does not implement :py:func:`!template_config`

    """

    def __init__(self):
        """Call :py:func:`template_config`."""
        self.template_config()

    def generate(self, job_dir, out_dir):
        """Render a report and output to given directory.

        The whole process breaks down into follwoing parts:

        1. read NGS result as :py:class:`~ngcloud.info.JobInfo`
        2. render report, covered by :py:func:`render_report`
        3. copy template-related static files such as JS and CSS
           into output dir, covered by :py:func:`copy_static`
        4. copy stage-related static files into output dir.
           Call each :py:func:`Stage.copy_static` respectively
        5. output rendered reports into output dir, covered by
           :py:func:`output_report`

        Notes
        -----
        **Override this function with care.** You might break the logic.

        """
        self.job_info = JobInfo(job_dir)
        self.out_dir = out_dir

        self.report_root = self.out_dir / ('report_%s' % self.job_info.id)
        logger.info(
            "Get a new job folder"
            "id: {0.id} type: {0.type}".format(self.job_info)
        )

        if not self.report_root.exists():
            self.report_root.mkdir(parents=True)

        # create stage instances
        self._stages = [
            Stage(self.job_info, self.report_root)
            for Stage in self.stage_template_cls
        ]

        self.render_report()

        # copy template's static files
        self.copy_static()

        # copy stage's static files
        for stage in self._stages:
            stage.copy_static()

        # write rendered report html to files
        self.output_report()

    def render_report(self):
        """Put real results into report template and return rendered html."""

        self.report_html = dict()
        for stage in self._stages:
            self.report_html[stage.template_name] = stage.render()

    def copy_static(self):
        """Copy template statics files to output dir."""
        shutil.copytree(
            strify_path(self.static_root),
            strify_path(self.report_root / 'static')
        )

    def output_report(self):
        """Output rendered htmls to output directory.

        No original data is involved, just some file I/Oing.
        """
        for name, content in self.report_html.items():
            with open(self.report_root / '{}.html'.format(name), 'w') as f:
                f.write(content)

    @abc.abstractmethod
    def template_config(self):
        """Setup configuration for report templates.

        *Always* override this method.
        Also, two instance attributes should be setted here:

        - :py:attr:`stage_template_cls`
        - :py:attr:`static_root`

        Examples
        --------

        .. code-block:: python3

            def template_config(self):
                self.stage_template_cls = [IndexStage, MyStage]
                self.static_root = "mypipe/report/static"

        One could also put the extra logics here for custom report,
        since this function will always be called by :py:func:`!__init__`

        .. py:attribute:: stage_template_cls

            (List of class name) Store the sequence of stages in use.
            Specify names of subclass of :py:class:`Stage`

            For example,

            .. code-block:: python3

                from ngcloud.pipe.common import InextStage, QCStage

                # inside template_config()
                self.stage_template_cls = [IndexStage, QCStage]

            One only needs to pass in the name of the stage class,
            not initiate the stage class.
            See :py:class:`Stage` for how to write a new stage class

        .. py:attribute:: static_root

            :py:class:`~pathlib.Path` to root dir of report static files,
            such as JS, CSS files for making html pages.

            For example,

            .. code-block:: python3

                # inside template_config()
                self.static_root = Path('ngreport/static')
                # below it has js/, css/, imgs/ subfolders

            Take care if the path is inside your package or inside the same
            folder as the Python script. One could use ``__file__``
            to determine where the script locates.

        """
        self.stage_template_cls = [Stage, Stage]
        self.static_root = Path()


def generate(pipe_report_cls, job_dir, out_dir, verbosity=0):
    """Generate a NGCloud report.

    For :ref:`normal usage <ngreport>`, one can use :command:`ngreport` command
    instead of calling this Python function directly.

    Parameters
    ----------
    pipe_report_cls: str
        Name of the Python class to generate the report of certain pipeline.
    job_dir: path-like object
    out_dir: path-like object
    verbosity: int
        How noisy the log will be

    Notes
    -----
    To extend NGCloud with your custom pipeline,
    inherit :py:class:`Report` and call this function manually.

    """
    # read in the pipeline class
    pipe_module_name, pipe_class_name = pipe_report_cls.rsplit('.', 1)
    pipe_module = importlib.import_module(pipe_module_name)
    PipeReport = getattr(pipe_module, pipe_class_name)

    if not issubclass(PipeReport, Report):
        raise TypeError(
            "pipe_report_cls: {} should be inherited from"
            "ngcloud.report.Report".format(pipe_report_cls)
        )

    job_dir = Path(job_dir)
    out_dir = Path(out_dir)

    # validate job_dir
    if not job_dir.exists():
        raise FileNotFoundError(
            'Job info folder: {} does not exist!'.format(job_dir)
        )
    if not job_dir.is_dir():
        raise NotADirectoryError(
            'Expect job info to be dir: {}'.format(job_dir)
        )

    report = PipeReport()
    report.generate(job_dir, out_dir)


def main():

    # setup console logging
    console = logging.StreamHandler()
    console.setFormatter(ng._log_formatter)
    logger.addHandler(console)

    args = docopt(_SCRIPT_DOC, version=ng.__version__)

    # set logging level
    if args['--verbose'] == 1:
        loglevel = logging.INFO
    elif args['--verbose'] >= 2:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
    console.setLevel(loglevel)

    logger.debug("Get command line arguments: {!r}".format(dict(args)))

    pipe_type = args['--pipe']
    # validate pipe_type
    if pipe_type not in AVAIL_PIPES:
        raise ValueError(
            "Unknown pipeline type: {}".format(pipe_type)
        )
    pipe_report_cls = AVAIL_PIPES[pipe_type]

    job_dir = Path(args['<job_dir>'])
    out_dir = Path(
        args['<out_dir>'] if args['<out_dir>'] else args['--outdir']
    )
    verbosity = args['--verbose']

    generate(pipe_report_cls, job_dir, out_dir, verbosity)

if __name__ == '__main__':
    main()
