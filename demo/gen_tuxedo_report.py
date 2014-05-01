from jinja2 import Environment, FileSystemLoader
# from tempfile import mkdtemp
from pathlib import Path
import shutil
import logging

# Jinja2 setup
report_loader = FileSystemLoader('report/templates')
env = Environment(loader=report_loader, extensions=['jinja2.ext.with_'])

def locate_static(path):
    return 'static/%s' % path

env.globals['static'] = locate_static


def copy_static(output_p, statc_dir='report/static'):
    shutil.copytree(statc_dir, str(output_p / 'static'))


def cleanup_output(output_p):
    if not output_p.exists:
        output_p.mkdir()
        return

    logging.info('Remove previous outputs under output')
    pre_output = [str(p) for p in output_p.iterdir()
                  if p.is_dir() and p.name.startswith('report_')]
    # remove all previous output
    for pre in pre_output:
        shutil.rmtree(pre)

    logging.warn(
        'The following ouput dir has been removed: %s' % ', '.join(pre_output)
    )


# Template in use setup
TPL_NAME = ['index', 'qc', 'tophat']  # , 'cufflinks']

report_tpl = {
    k: env.get_template('%s.html' % k)
    for k in TPL_NAME
}

report_out = dict()


def render_report():
    config = {
        'project_id': 9527,
    }
    # render out report
    report_out['index'] = report_tpl['index'].render(**config)
    report_out['qc'] = report_tpl['qc'].render(**config)
    report_out['tophat'] = report_tpl['tophat'].render(**config)


def output_report(base_dir):
    for name, content in report_out.items():
        with open(str(base_dir / '{}.html'.format(name)), 'w') as f:
            f.write(content)

    return base_dir / 'index.html'


def gen_report(output_p):
    # create new folder, copy static files
    base_dir = output_p / 'report_dev'
    # Path(mkdtemp(prefix='report_', dir=str(output_p)))
    if not base_dir.exists():
        base_dir.mkdir()
    copy_static(base_dir)

    render_report()
    index_p = output_report(base_dir)
    return base_dir, index_p


_CAVEAT_MSG = '''\
New output result is under {!s}.

The folder can be downloaded and viewed locally.
Quick remainder for serving current folder through http:

    $ python3 -m http.server
    # Serving HTTP on 0.0.0.0 port 8000 ...
'''

if __name__ == '__main__':
    output_p = Path('output')
    if not output_p.exists():
        output_p.mkdir()
    else:
        cleanup_output(output_p)

    base_dir, index_p = gen_report(output_p)
    print(_CAVEAT_MSG.format(base_dir))
