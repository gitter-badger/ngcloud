import re
import sys
import os.path
import importlib
import shutil
from pathlib import Path
import abc
import logging
from docopt import docopt
import jinja2
import ngcloud as ng
from ngcloud.util import (
    strify_path, open, is_pathlike, merged_copytree,
    copy, discover_file_by_patterns
)
from ngcloud.info import JobInfo

logger = ng._create_logger(__name__)

AVAIL_PIPES = {
    'tuxedo': 'ngcloud.pipe.tuxedo.TuxedoReport'
}

_SCRIPT_DOC = """\
NGCloud report generator for differenct NGS analysis pipelines.

Usage:
    ngreport [-p <pipeline>] <job_dir> [<out_dir>] [-v ...] [options]
    ngreport [-p <pipeline>] <job_dir> [-o <out_dir>] [-v ...] [options]
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
    --color             Produce colorful logs, require colorlog
    --log-time          Add time stamp in log

"""

_CAVEAT_MSG = '''\
New output result is under {!s}.

The folder can be downloaded and viewed locally.
Quick remainder for serving current folder through http:

    $ python3 -m http.server
    # Serving HTTP on 0.0.0.0 port 8000 ...
'''

__doc__ = """\
Base classes to produce NGCloud report

.. autosummary::

    Stage
    Report
    gen_report
    main
"""

class Stage(metaclass=abc.ABCMeta):
    """base class of NGCloud stage of a report.

    A stage in report usually maps to a NGS tool used in a pipeline,
    and this tool generates meaningfull output of log files that are need for
    further analysis.

    :py:class:`Stage` is a connection between Jinja2's template system
    with NGS results. Therefore one can write the logics about how to extract
    information out of a tool(stage) output and pass those information to
    Jinja2's template with some variables.

    Examples
    --------
    A minimal stage for rendering single template, no static file copying::

        class SimpleStage(Stage):
            template_find_paths = ['path/to/templates']
            template_entrances = 'simple.html'
            # so it render template 'path/to/templates/simple.html'

    With static file copying

    .. code-block:: python3

        class CopyStaticStage(Stage):
            template_find_paths = ['path/to/templates']
            template_entrances = 'copy_static.html'

            # all related result files are under
            # <result_root>/copy_static/
            result_foldername = 'copy_static'
            embed_result_joint = [{
                'src': 'joint',
                'patterns': ['foo'],
                'dest': 'copy_static'
            }]
            # will copy <result_root>/copy_static/joint/foo
            #   -> <report_root>/static/copy_static/foo

            embed_result_persample = [{
                'src': 'each',
                'patterns': ['baz']
                'dest': 'copy_static'
            }]
            # for every sample <sample>, copy
            # <result_root>/copy_static/each/<sample>/baz
            #   -> <report_root>/static/copy_static/<sample>/baz

    Attributes
    ----------
    template_entrances : (list of) str
        Template names passed to Jinja2 to call render()
    template_find_paths : (list of) path-like object
        Paths in order to load templates
    report_root : Path object
        Path to where report will be under
    embed_result_joint : list of dict
        Embeded joint static file copying description
    embed_result_persample : list of dict
        Embedded per sample static file copying description
    result_foldername : str
        Folder name to the NGS result of this stage
    job_info : JobInfo object
        Information about how the NGS result is run
    result_info : dict object
        Key-value pairs storing parsed NGS result
    result_root : Path object
        Path to stage's result dir

    Methods
    -------
    __init__
    copy_static
    copy_static_joint
    copy_static_persample
    parse
    render

    """
    template_entrances = ['stage.html']
    """Name of templates that will trigger :py:meth:`render`.

    In most cases, there is only *one* entry point, so a stage
    corresponds to one HTML page in report.
    However, if this attribute contains a list of template names
    then multiple HTML pages will be produced.
    """

    template_find_paths = ['report/templates']
    """Path to root of templates.

    These paths are passed to :py:class:`jinja2.FileSystemLoader` in order.
    Generally if one is going to extend a NGCloud pipeline,
    then one shoud supply the NGCloud's template root path and
    custom templates path. See :ref:`extend_builtin_pipe` for more info.
    """

    embed_result_joint = []
    """List of description for joint result embedded into report.

    Each element of list (say *desc*) is a dict having structure::

        desc = {
            'src': 'in_result',
            'patterns': ['foo*', '**/bar'],
            'dest': 'in_report/deep'
        }
        embed_result_joint = [descA, descB, ...]

    - **src**: path appended after :attr:`self.result_root <result_root>`
    - **patterns**: list of file patterns support
      ``*``, ``**``, ``?`` globbing syntax
    - **dest**: path appended under report static files, usually
      ``<report_root>/static/``

    All files matching *patterns* under *src* will be copied to *dest*.

    :meth:`copy_static_joint` accesses this attribute.

    .. versionadded:: 0.3
    """

    embed_result_persample = []
    """List of description for per sample result embedded into report.

    Its structure is similar to :attr:`embed_result_persample` while how
    it works is quite different. If we use the above example::

        desc = {
            'src': 'in_result',
            'patterns:': ['foo*', '**/bar'],
            'dest': 'in_report/deep'
        }
        embed_result_persample = [descA, descB, ...]

    They differ in how NGCloud find the paths:

    - **src**: path appended after :attr:`self.result_root <result_root>`
      *plus* sample's full name
    - **dest**: path appended under report static files *plus* samples's
      full name.

    And whole procedure will be performed for each sample, so one will
    get multiple sets of files matching *patterns*.

    :meth:`copy_static_persample` accesses this attribute.

    .. versionadded:: 0.3
    """

    result_foldername = ''
    """Folder name to the result of this stage.

    Number prefix of the folder can be excluded. Therefore, setting
    **"mystage"** can recognized all following folders:
    mystage, 3_mystage, 05_mystage.

    If an unique folder matching the pattern is found, the path
    to this folder is stored in :attr:`self.result_root <result_root>`.

    Otherwise, *ValueError* is raised if none or more than two
    matched folder are found.

    .. versionadded:: 0.3
    """

    def __init__(self, job_info, report_root):
        """Initiate a Stage object.

        Here NGS result info and path to gerenerate report is passed.

        .. py:attribute:: job_info
            :annotation: = job_info

            :py:class:`~ngcloud.info.JobInfo` object.

        .. py:attribute:: report_root
            :annotation: = report_root

            :py:class:`~pathlib.Path` object.

        .. py:attribute:: result_info
            :annotation: = dict()

            A :class:`!dict` object to store NGS result info. See :meth:`parse`
            for more information.

            .. note:: Key names should follow Python argument naming rule.

        .. py:attribute:: result_root
            :annotation: = join_info.root_path + result_foldername

            :class:`~pathlib.Path` object to the stage result root folder.

            This attribute is automatically set by finding the matched
            foldername based on :attr:`result_foldername`
        """
        logger.info("Initating new stage {}".format(type(self).__name__))
        self._setup_jinja2()
        if is_pathlike(self.template_entrances):
            tpls = [self.template_entrances]
        else:
            tpls = self.template_entrances
        self._templates = {tpl: self._env.get_template(tpl) for tpl in tpls}

        self.job_info = job_info
        self.report_root = report_root
        self.result_info = dict()
        logger.debug("... Loacate result folder path")
        self.result_root = self._locate_result_folder()
        self.parse()
        logger.debug("... stage initiated".format(type(self).__name__))

    def _setup_jinja2(self):
        try:
            _template_paths = strify_path(self.template_find_paths)
        except TypeError:
            _template_paths = [
                strify_path(p) for p in self.template_find_paths
            ]
        logger.debug(
            "Jinja2 reads templates from {}".format(_template_paths)
        )
        self._report_loader = jinja2.FileSystemLoader(_template_paths)
        self._env = jinja2.Environment(
            loader=self._report_loader,
            extensions=['jinja2.ext.with_'],
        )
        self._env.globals['static'] = self._template_static_path

    def _locate_result_folder(self):
        if not self.result_foldername:
            logger.warn(
                "No result foldername set for stage {}, "
                "using {!s}"
                .format(self.__class__.__name__, self.job_info.root_path)
            )
            return self.job_info.root_path

        folder_pattern = r"^(\d+_|){}$".format(self.result_foldername)
        logger.debug(
            "Result foldername regex pattern: {}".format(folder_pattern))
        valid_name = re.compile(folder_pattern).match

        stage_result_path = [
            p for p in self.job_info.root_path.iterdir()
            if valid_name(p.name)
        ]
        if not stage_result_path:
            raise ValueError("No matched foldername found of pattern {}"
                             .format(self.result_foldername))
        if len(stage_result_path) > 1:
            raise ValueError(
                "Duplicated stage result folders found: {} of pattern {}"
                .format(stage_result_path, self.result_foldername))
        return stage_result_path[0]

    def _template_static_path(self, *path_parts):
        return Path('static', *path_parts).as_posix()

    def render(self):
        """Render the templates of this stages and return HTML output.

        It calls each template's render() functio with arguments
        :attr:`self.job_info <job_info>`, :attr:`self.result_info
        <result_info>` and unpacked :attr:`self.result_info <result_info>`.
        So one can access the following variables in their templates:

        - `job_info`
        - `result_info`
        - keys of `result_info`

        Internally, it calls :py:meth:`jinja2.Template.render`.

        How it works can be conceptually viewed as::

            return tpl.render(
                job_info=self.job_info, result_info=self.result_info,
                **self.result_info)

        Each templates specified in :attr:`template_entrances`
        will be rendered. The HTML output will be stored in a dict
        with key using its filename::

            {'stage.html': '<html>...</html>'}


        Returns
        -------
        :class:`!dict` object

            Key-value pairs that maps entrance template name to
            rendered template HTML content.

        Examples
        --------

        If a stage has NGS results parsed,

            >>> mystage = Stage()
            >>> mystage.result_info.update(
            ...     {'map_rate': '0.556', 'idfy_genes': '633'})
            >>> mystage.render()

        The arugments passed to Jinja2's render() are::

            tpl.render(job_info=mystage.job_info, result_info=result_info,
                       map_rate='0.556', idfy_genes='633')

        """
        return {
            tpl_name: tpl.render(
                job_info=self.job_info, result_info=self.result_info,
                **self.result_info)
            for tpl_name, tpl in self._templates.items()
        }

    def parse(self):
        """Parse the NGS result and store in :attr:`self.result_info <result_info>`

        By default, no action is taken in this method.
        """
        pass

    def copy_static(self):
        """Copy stage-specific static files under report folder.

        It calls :meth:`copy_static_joint` and :meth:`copy_static_persample`
        to copy static files. Their behavior differ slightly.

        - **copy_static_joint()** copy those files that are *jointly* produced
          based on all samples. So those files should uniquely exist in this
          stage.

          For example, differential expression comparison for each pairs
          of samples. The comparison result no longer belongs to any sample
          alone but stage-wide.

          It takes the file description from :attr:`embed_result_joint`.

        - **copy_static_persample()** copy those files of *each sample*.
          If there are total 4 samples, then there should be 4 sets of such
          files.

          For example, quality check stage will check each sample and produce
          their own quality information.

          It takes the file description from :attr:`embed_result_persample`.

        By default, nothing will be copied because both embbed_result are
        default to empty list.

        Notes
        -----

        If a stage doesn't not need to copy any static files or one type of the
        static files is not required, one could simply passing a empty list to
        **embed_result_joint** or **embed_result_persample** to skip copying.
        There is no need to override this function.

        .. versionchanged:: 0.3
            Add default behavior

        """
        self.copy_static_joint()
        self.copy_static_persample()

    def copy_static_joint(self):
        """Copy static files that are jointly produced from all samples.

        It reads the result information to be embedded from attribute
        :attr:`embed_result_joint`.

        For each description dict, say `desc`, in the list
        **embed_result_joint**, it finds files with
        each globbing pattern::

            <self.result_root>/desc['src']/desc['patterns']

        and copies them to::

            <self.report_root>/static/desc['dest']/

        Examples
        --------
        For stage

        .. code-block:: python3

            class JointStage(Stage):
                embed_result_joint = [{
                    'src': 'from',
                    'patterns': ['*.jpg', 'sub_dir/bar'],
                    'dest': 'to'
                }, {
                    'src': 'deep/src',
                    'patterns': 'foo',
                    'dest': 'deeper/alt'
                }]

        the static files are mapped::

            <result_root>/from/*.jpg       -> <report>/static/to/*.jpg
            <result_root>/from/sub_dir/bar -> <report>/static/to/bar
            <result_root>/deep/src/foo     -> <report>/static/deeper/alt/foo

        .. versionadded:: 0.3
        """
        for desc in self.embed_result_joint:
            src_root = self.result_root / desc['src']
            dest_root = self.report_root / 'static' / desc['dest']
            if not dest_root.exists():
                dest_root.mkdir(parents=True)

            file_list = discover_file_by_patterns(src_root, desc['patterns'])
            for fp in file_list:
                copy(fp, dest_root)

    def copy_static_persample(self):
        """Copy statics file that are spearately produced by each sample.

        It reads the result information to be embedded from attribute
        :attr:`embed_result_persample`.

        For each description dict, say **desc**, in the list
        *embed_result_persample*, it finds files
        with each globbing patterns for each *sample*::

            <self.result_root>/desc['src']/sample.full_name/desc['patterns']

        and copies them to::

            <self.report_root>/static/desc['dest']/sample.full_name/

        Examples
        --------

        If we have samples with full name: *A_R1*, and *B*. For stage

        .. code-block:: python3

            class PerSampleStage(Stage):
                embed_result_persample = [{
                    'src': 'from',
                    'patterns': ['foo', 'bar'],
                    'dest': 'to'
                }]

        the static files are mapped::

            <result_root>/from/A_R1/foo -> <report>/static/to/A_R1/foo
            <result_root>/from/A_R1/bar -> <report>/static/to/A_R1/bar
            <result_root>/from/B/foo    -> <report>/static/to/B/foo
            <result_root>/from/B/bar    -> <report>/static/to/B/bar

        .. versionadded:: 0.3
        """
        for desc in self.embed_result_persample:
            all_src_root = self.result_root / desc['src']
            all_dest_root = self.report_root / 'static'

            for sample in self.job_info.sample_list:
                # TODO: fuzzy match sample.name
                sp_src_root = all_src_root / sample.full_name
                sp_dest_root = all_dest_root / desc['dest'] / sample.full_name
                sp_dest_root.mkdir(parents=True)

                file_list = discover_file_by_patterns(
                    sp_src_root, desc['patterns'])
                for fp in file_list:
                    copy(fp, sp_dest_root)


class Report(metaclass=abc.ABCMeta):
    """NGCloud report base class of every pipeline.

    To combind custom pipeline with :command:`ngreport`,
    :py:meth:`__init__` signature must match :py:class:`Report`.
    Setup the custom logics in :py:meth:`template_config`

    Raises
    ------
    TypeError
        When initiate this class directly,
        or subclass does not implement :py:func:`!template_config`

    Attributes
    ----------
    job_info : Path object
    out_dir : Path object
    report_root : Path object
    stage_classnames : list of class
        List of stage class name in order used in for this pipeline report.
    static_roots : Path object
        Path to the template static file dir

    Methods
    -------
    __init__
    template_config
    generate
    render_report
    copy_static
    output_report

    """
    stage_classnames = [Stage]
    """(List of class name) Store the sequence of stages in use.

    Specify names of subclass of :py:class:`Stage`.
    One only needs to pass names of the stage class,
    don't initiate the stage class.
    ::

        stage_classnames = [IndexStage, QCStage]

    See :py:class:`Stage` for how to write a new stage class
    """

    static_roots = ['']
    """(list of) path-like object to root dir of report static files,
    such as JS, CSS files for making html pages.

    For example,
    ::

        static_roots = Path('my/report/static')

    where below :file:`my/report/static` has needed js, css, img files.

    A common case will be to extend existed pipelines, then both
    shared static files and custom static files can be uesd
    by giving a list of paths to root of static files.
    ::

        from ngcloud.pipe import get_shared_static_root  # get builtin static
        static_roots = [get_shared_static_root(), '/path/to/my/static']

    See :ref:`extend_builtin_pipe` for more inforation.
    """

    def __init__(self):
        """Call :py:func:`template_config`. Don't override me."""
        logger.debug(
            "New report {} object has been initiated"
            .format(type(self).__name__)
        )
        self.template_config()

    def generate(self, job_dir, out_dir):
        """Render a report and output to given directory.

        The whole process breaks down into follwoing parts:

        1. read job info as :py:class:`~ngcloud.info.JobInfo`
        2. parse NGS result, covered by :meth:`parse`
        2. render report, covered by :py:meth:`render_report`
        3. copy template-related static files such as JS and CSS
           into output dir, covered by :py:meth:`copy_static`
        4. copy stage-related static files into output dir.
           Call each :py:meth:`Stage.copy_static` respectively
        5. output rendered reports into output dir, covered by
           :py:meth:`output_report`

        .. warning::

            **Override this function with care.** You might break the logic.

        """
        logger.info(
            "Generate report from job result {!s} under {!s}"
            .format(job_dir, out_dir)
        )
        self.job_info = JobInfo(job_dir)
        self.out_dir = Path(out_dir)

        self.report_root = self.out_dir / ('report_%s' % self.job_info.id)
        logger.info(
            "Get a new job folder"
            "id: {0.id} type: {0.type}".format(self.job_info)
        )

        if self.report_root.exists():
            logger.warn(
                "Report root {!s} has already existed! Overwriting..."
                .format(self.report_root)
            )
            shutil.rmtree(self.report_root.as_posix())
        self.report_root.mkdir(parents=True)

        # create stage instances
        self._stages = [
            Stage(self.job_info, self.report_root)
            for Stage in self.stage_classnames
        ]

        logger.info("Render report templates")
        self.render_report()

        logger.info("Copying report static files")
        self.copy_static()

        logger.info("Copying each stage's static files")
        for stage in self._stages:
            stage.copy_static()

        logger.info("Write rendered templates to file")
        self.output_report()

    def render_report(self):
        """Put real results into report template and return rendered html."""
        self.report_html = dict()
        for stage in self._stages:
            self.report_html.update(stage.render())

    def copy_static(self):
        """Copy template statics files to output dir.

        Files under each path specifed by :py:attr:`static_roots`
        will be copied to folder :file:`static` below :py:attr:`report_root`.
        """
        if is_pathlike(self.static_roots):
            _static_roots = [self.static_roots]
        else:
            _static_roots = self.static_roots
        merged_copytree(_static_roots, self.report_root / 'static')

    def output_report(self):
        """Output rendered htmls to output directory.

        No original data is involved, just some file I/Oing.
        """
        for name, content in self.report_html.items():
            with open(self.report_root / '{}'.format(name), 'w') as f:
                f.write(content)

    def template_config(self):
        """Setup configuration for report templates.

        One could also put the extra logics here for custom report,
        since this function will always be called by :py:func:`__init__`
        """
        pass


def gen_report(pipe_report_cls, job_dir, out_dir):
    """Generate a NGCloud report.

    For :ref:`normal usage <ngreport>`, one can use :command:`ngreport` command
    instead of calling this Python function directly.

    Parameters
    ----------
    pipe_report_cls: str
        Name of the Python class to generate the report of certain pipeline.
    job_dir: path-like object
    out_dir: path-like object

    """
    # read in the pipeline class
    logger.debug("Get pipeline class: {}".format(pipe_report_cls))
    pipe_module_name, pipe_class_name = pipe_report_cls.rsplit('.', 1)
    logger.info(
        "Get report class {} from module {}"
        .format(pipe_class_name, pipe_module_name)
    )
    pipe_module = importlib.import_module(pipe_module_name)
    PipeReport = getattr(pipe_module, pipe_class_name)

    if not issubclass(PipeReport, Report):
        logger.warn(
            "Unaccepted report class {} being passed, "
            "should be subclass of ngcloud.report.Report"
        )
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
            'Expect path to job info a valid directory: {}'.format(job_dir)
        )

    report = PipeReport()
    report.generate(job_dir, out_dir)


def main(argv=None):
    """Store the logics for :command:`ngreport`.

    If one just wants the :command:`ngreport`'s functionality, try call
    :func:`gen_report` not this function.

    Anyway, If **args** is passed, it runs like **ngreport** is called.
    *args* should be a list that passes to :func:`subprocess.check_call`
    excluding the first element (program name),

        >>> main(argv=['-p', 'ext_pipe.myReport', 'job_mine', '--color'])

    Notes
    -----
    If one wants to emit log messages in their custom modules, NGClouds now
    recognizes them by default.

    .. code-block:: python3

        # in ext_pipe.py
        import logging
        logger = logging.getLogger("external.{}".format(__name__))
        from ngcloud.report import main as _main

        class MyStage(Stage):
            def parse(self):
                logger.warning("My custom warnning")  # will appear in the log

        def main():
            argv = ["some", "args", "to", "ngreport"]
            _main(argv=argv)  # If argv not specified, read from sys.argv[1:]

    However, the logging messages will *pollutes* stderr.
    If that is not desired, use :func:`gen_report`.
    You can get all NGCloud's log to stderr by

    .. code-block:: python3

        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(
            "[%(levelname)s][%(name)s] %(message)s"))
        ng_logger = logging.getLogger("ngcloud")
        ng_logger.addHandler(console)
        ng_logger.setLevel(logging.INFO)

    .. seealso::

        See module Python standard library :py:mod:`logging` for its flexible
        logging functionality. You are encouraged to use it.

    .. versionchanged:: 0.3

        Add **argv**; include external loggers.

    """
    # setup console logging
    console = logging.StreamHandler()
    all_loggers = logging.getLogger()
    all_loggers.addHandler(console)

    # read arguments from command line
    if argv:
        args = docopt(_SCRIPT_DOC, argv=argv, version=ng.__version__)
    else:
        args = docopt(_SCRIPT_DOC, version=ng.__version__)

    # set logging level
    if args['--verbose'] == 1:
        loglevel = logging.INFO
    elif args['--verbose'] >= 2:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
    all_loggers.setLevel(loglevel)

    # set log format
    log_fmt = '[%(levelname)-7s][%(name)-8s][%(funcName)-8s] %(message)s'
    if args['--log-time']:
        log_fmt = '[%(asctime)s]' + log_fmt

    log_formatter = logging.Formatter(
        log_fmt,
        '%Y-%m-%d %H:%M:%S'
    )

    color_log_fmt = (
        '%(log_color)s%(levelname)-7s%(reset)s %(cyan)s%(name)-8s%(reset)s '
        '%(log_color)s[%(funcName)s]%(reset)s %(message)s'
    )
    if args['--log-time']:
        color_log_fmt = '%(asctime)s ' + color_log_fmt

    if args['--color']:
        try:
            import colorlog
            log_color_formatter = colorlog.ColoredFormatter(
                color_log_fmt,
                '%Y-%m-%d %H:%M:%S',
                log_colors=colorlog.default_log_colors
            )
            console.setFormatter(log_color_formatter)
        except ImportError:
            console.setFormatter(log_formatter)
            logger.warn(
                "Color logs require colorlog, "
                "try pip install colorlog or colorlog[windows] on Windows"
            )
    else:
        console.setFormatter(log_formatter)

    logger.debug("Get command line arguments: {!r}".format(dict(args)))

    # set pipeline to use
    pipe_type = args['--pipe']
    if pipe_type in AVAIL_PIPES:
        pipe_report_cls = AVAIL_PIPES[pipe_type]
    else:
        logger.info(
            "Pipeline type {} is not in AVAIL_PIPES, "
            "pass it as a Python class name".format(pipe_type)
        )
        pipe_report_cls = pipe_type

    job_dir = Path(args['<job_dir>'])
    out_dir = Path(
        args['<out_dir>'] if args['<out_dir>'] else args['--outdir']
    )

    # FIXME: custom pipeline cannot be find if they are not official packages
    # therefore where the ngreport being called should be added into sys.path
    # currently is a hack. More elegant way should be used
    sys.path.append(os.path.abspath('.'))
    logger.debug(
        "Inject current path into sys.path. "
        "Now find packages under paths: {!r}".format(sys.path)
    )

    # called real function to generate report
    gen_report(pipe_report_cls, job_dir, out_dir)

    logger.info("Job successfully end. Print message")
    print(_CAVEAT_MSG.format(out_dir))


if __name__ == '__main__':
    main()
