import shutil
import logging
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from ngparser.info import JobInfo
from ngparser.util import expanduser

_CAVEAT_MSG = '''\
New output result is under {!s}.

The folder can be downloaded and viewed locally.
Quick remainder for serving current folder through http:

    $ python3 -m http.server
    # Serving HTTP on 0.0.0.0 port 8000 ...
'''

# Jinja2 setup
report_loader = FileSystemLoader('report/templates')
env = Environment(loader=report_loader, extensions=['jinja2.ext.with_'])
env.globals['static'] = lambda path: 'static/%s' % path

# Template in use setup
TPL_NAME = ['index', 'qc', 'tophat']  # , 'cufflinks']

REPORT_TPL = {
    k: env.get_template('%s.html' % k)
    for k in TPL_NAME
}

def copy_static(report_root, statc_dir='report/static'):
    if not report_root.exists():
        report_root.mkdir()

    shutil.copytree(statc_dir, str(report_root / 'static'))


def cleanup_output(output_root):
    if not output_root.exists:
        output_root.mkdir()
        return

    logging.info('Remove previous outputs under output')
    previous_output = [
        str(p) for p in output_root.iterdir()
        if p.is_dir() and p.name.startswith('report_')
    ]
    logging.warn(
        'These ouput reports will be removed: %s' % ', '.join(previous_output)
    )
    for pre in previous_output:
        shutil.rmtree(pre)


def render_report(job_info):
    """Put real result into report template, and return the rendered html."""
    report_html = dict()

    # render out report
    report_html['index'] = REPORT_TPL['index'].render(job_info=job_info)
    report_html['qc'] = REPORT_TPL['qc'].render(job_info=job_info)
    report_html['tophat'] = REPORT_TPL['tophat'].render(job_info=job_info)

    return report_html

def output_report(report_root, report_html):
    """Output the render html to the output location.

    So no original data is involved, just some file I/O.
    """
    for name, content in report_html.items():
        with open(str(report_root / '{}.html'.format(name)), 'w') as f:
            f.write(content)

    return report_root / 'index.html'  # return the path to front page


def gen_report(job_root, output_root):
    """Whole process of reading a real result, then output report.

    The process can be splitted into 3 parts:

    1. read original data (covered by ngparser)
    2. render report (:func:`render_report`)
    3. output report under output_root (:func:`output_report`)

    """

    job_info = JobInfo(job_root)
    report_root = output_root / ('report_%s' % job_info.id)
    logging.info(
        "Get a new job folder id: {0.id} type: {0.type}".format(job_info)
    )

    report_html = render_report(job_info)

    copy_static(report_root)
    index_p = output_report(report_root, report_html)

    return report_root, index_p


if __name__ == '__main__':
    output_root = Path('output')
    cleanup_output(output_root)
    if sys.platform == "darwin":
        JOB_PATH = Path(
            expanduser("~/Documents/biocloud_datasets/job_9527_tuxedo"))
    elif sys.platform.startswith("linux"):
        JOB_PATH = Path(
            expanduser("~/dataset/biocloud/job_9527_tuxedo"))

    report_root, index_p = gen_report(JOB_PATH, output_root)
    print(_CAVEAT_MSG.format(report_root))
