import shutil
import logging
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from ngcloud.info import JobInfo
from ngcloud.util import expanduser, copy, strify_path, open

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
        strify_path(p) for p in output_root.iterdir()
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


def copy_static_qc(job_info, report_root):
    """Copy needed file for report in qc stage

    - qc summary img (not implemented)
    - qc img by sample

    """
    copy_static_qc_summary(job_info, report_root)
    copy_static_qc_sample(job_info, report_root)


def copy_static_qc_summary(job_info, report_root):
    """Copy QC summary pics to static/qc_overall"""

    _REQUIRE_FILE = [
        'per_base_quality.png',
        'per_base_sequence_content.png',
    ]
    _DST_ROOT = report_root / 'static' / 'qc_overall'
    _SRC_ROOT = job_info.root_path / '1_fastqc' / 'overall'

    if not _DST_ROOT.exists():
        _DST_ROOT.mkdir(parents=True)

    for require_fp in _REQUIRE_FILE:
        copy(_SRC_ROOT / require_fp, _DST_ROOT)


def copy_static_qc_sample(job_info, report_root):
    """Copy QC sample pics to static/qc_sample/<sample_name>"""
    _REQUIRE_FILE_PATTERN = [
        '*.png'
    ]
    _DST_ROOT = report_root / 'static' / 'qc_sample'
    _SRC_ROOT = job_info.root_path / '1_fastqc' / 'output'

    # copy imgs from each sample run
    for sample in job_info.sample_list:
        # collect required file list
        require_fp_list = []
        for pattern in _REQUIRE_FILE_PATTERN:
            sp_root = _SRC_ROOT / "{}_fastqc".format(sample.name) / "Images"
            require_fp_list.extend(sp_root.glob(pattern))

        _dst_sample_dir = _DST_ROOT / sample.full_name / "pics"
        _dst_sample_dir.mkdir(parents=True)
        # copy based on the file list
        for fp in require_fp_list:
            copy(fp, _dst_sample_dir)


def output_report(report_root, report_html):
    """Output the render html to the output location.

    So no original data is involved, just some file I/O.
    """
    for name, content in report_html.items():
        with open(report_root / '{}.html'.format(name), 'w') as f:
            f.write(content)

    return report_root / 'index.html'  # return the path to front page


def gen_report(job_root, output_root):
    """Whole process of reading a real result, then output report.

    The process can be splitted into 3 parts:

    1. read original data (covered by ngcloud)
    2. render report (:func:`render_report`)
    3. output report under output_root (:func:`output_report`)
    4. copy required output file under /static folder.
       In this case, only qc stage is required. (:func:`copy_static_qc`)

    """

    job_info = JobInfo(job_root)
    report_root = output_root / ('report_%s' % job_info.id)
    logging.info(
        "Get a new job folder id: {0.id} type: {0.type}".format(job_info)
    )

    report_html = render_report(job_info)

    copy_static(report_root)
    copy_static_qc(job_info, report_root)
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
