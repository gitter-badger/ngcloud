import re
import logging
from pathlib import Path
from ngcloud.report import main as _main
from ngcloud.pipe import tuxedo
from ngcloud.util import open  # flake8: noqa

logger = logging.getLogger("external.%s" % __name__)

class TuxedoBaseStage(tuxedo.TuxedoBaseStage):
    template_find_paths = tuxedo.TuxedoBaseStage.template_find_paths[:]
    template_find_paths.insert(0, Path('templates'))

    @property
    def sample_group(self):
        return self.job_info.sample_group

class TophatStage(TuxedoBaseStage, tuxedo.TophatStage):
    pass

class TuxedoReport(tuxedo.TuxedoReport):
    stage_classnames = [
        tuxedo.IndexStage, tuxedo.QCStage, TophatStage
    ]
    static_roots = tuxedo.TuxedoReport.static_roots[:]
    static_roots.extend([
        '../../template_dev/dev/shared',
        '../../template_dev/dev/tuxedo'
    ])

def main():
    argv = [
        "-p", "next_tuxedo.TuxedoReport",
        "../job_tuxedo_minimal",
        "-vv", "--color"
    ]
    _main(argv=argv)

if __name__ == '__main__':
    main()
