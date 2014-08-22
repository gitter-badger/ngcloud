import logging
from pathlib import Path
from ngcloud.report import main as _main
from ngcloud.pipe import tuxedo
from ngcloud.util import open

logger = logging.getLogger("external.%s" % __name__)

class TophatStage(tuxedo.TophatStage):
    template_find_paths = tuxedo.TuxedoBaseStage.template_find_paths[:]
    template_find_paths.insert(0, Path('template'))

class TuxedoReport(tuxedo.TuxedoReport):
    stage_classnames = [
        tuxedo.IndexStage, tuxedo.QCStage, TophatStage
    ]
    static_roots = tuxedo.TuxedoReport.static_roots[:]
    static_roots.append('../../template_dev/tuxedo')

def main():
    argv = [
        "-p", "next_tuxedo.TuxedoReport",
        "../job_tuxedo_minimal",
        "-vv", "--color"
    ]
    _main(argv=argv)

if __name__ == '__main__':
    main()
