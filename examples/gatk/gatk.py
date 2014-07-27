from pathlib import Path
from ngcloud import _create_logger
from ngcloud.report import Stage, Report
from ngcloud.pipe import (
    get_shared_template_root, get_shared_static_root,
    _get_builtin_template_root
)
from ngcloud.pipe import tuxedo

logger = _create_logger(__name__)
_here = Path(__file__).parent

class GATKBaseStage(Stage):
    template_find_paths = [
        _here / "report" / "templates",
        get_shared_template_root(),
    ]

class IndexStage(GATKBaseStage):
    template_entrancename = 'index.html'

class QCStage(tuxedo.QCStage):
    template_find_paths = GATKBaseStage.template_find_paths
    template_find_paths.append(
        _get_builtin_template_root() / 'tuxedo'
    )

class AlignStage(GATKBaseStage):
    template_entrancename = 'align.html'

class GATKStage(GATKBaseStage):
    template_entrancename = 'gatk.html'

class GATKReport(Report):
    def template_config(self):
        self.stage_template_cls = [
            IndexStage,
            QCStage,
            AlignStage,
            GATKStage
        ]
        self.static_roots = [
            _here / 'report' / 'static',
            get_shared_static_root(),
        ]