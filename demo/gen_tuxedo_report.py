from jinja2 import Environment, FileSystemLoader
from tempfile import mkdtemp
from pathlib import Path
import shutil
import subprocess as sp
import sys

# Jinja2 setup
report_loader = FileSystemLoader('report/templates')
env = Environment(loader=report_loader)

def locate_static(path):
    return 'static/%s' % path

env.globals['static'] = locate_static


# Template in use setup
TPL_NAME = ['index']  # , 'fastqc', 'tophat', 'cufflinks']

report_tpl = {
    k: env.get_template('%s.html' % k)
    for k in TPL_NAME
}

report_out = dict()


def render_report():
    # render out report
    report_out['index'] = report_tpl['index'].render()


def output_report(base_dir):
    index_p = base_dir / 'index.html'
    with open(str(index_p), 'w') as f:
        f.write(report_out['index'])

    return index_p

def copy_static(output_p, statc_dir='report/static'):
    shutil.copytree(statc_dir, str(output_p / 'static'))

if __name__ == '__main__':
    output_p = Path('output')
    if not output_p.exists():
        output_p.mkdir()
    else:
        # remove all previous output
        shutil.rmtree(str(output_p))
        output_p.mkdir()

    render_report()

    base_dir = Path(mkdtemp(prefix='report_', dir='output'))
    index_p = output_report(base_dir)
    copy_static(base_dir)

    # open report dir in OSX
    if sys.platform.startswith('darwin'):
        sp.call(['open', str(index_p.resolve())])
