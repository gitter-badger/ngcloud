import logging
from pathlib import Path
from ngcloud.report import Report, main as _main
from ngcloud.pipe import get_shared_static_root, get_shared_template_root
from ngcloud.pipe.tuxedo import QCStage

logger = logging.getLogger("external.%s" % __name__)

class NewQCStage(QCStage):
    template_find_paths = [
        Path('report', 'templates'),
        get_shared_template_root(),
    ]
    template_entrances = 'newqc.html'
    embed_result_joint = []
    embed_result_persample = [
        {'src': '.',
         'patterns': ['Images/*.png'],
         'dest': 'qc_sample/pics'},
    ]

    def parse(self):
        for sample in self.job_info.sample_list:
            pass
        self.result_info['stage_mapping'] = [
            ('qc', 'newqc.html', 'Quality Control')
        ]


class QCOnly(Report):
    def __init__(self):
        logger.warning("Custom message")
        super(Report, self).__init__()
    stage_classnames = [NewQCStage]
    static_roots = [
        get_shared_static_root(),
    ]

def main():
    argv = [
        "-p", "newqc.QCOnly", "job_new_qc",
        "-vv", "--color"
    ]
    _main(argv=argv)

if __name__ == '__main__':
    main()
