from pathlib import Path
import ngcloud as ng
from ngcloud.report import Stage, Report

logger = ng._create_logger(__name__)
_here = Path(__file__).parent


class IndexStage(Stage):
    template_name = 'index'
    template_root = _here / 'report' / 'templates'

class QCStage(Stage):
    template_name = 'qc'
    template_root = _here / 'report' / 'templates'

class TophatStage(Stage):
    template_name = 'tophat'
    template_root = _here / 'report' / 'templates'

class TuxedoReport(Report):
    """NGCloud report class of Tuxedo pipeline."""

    def template_config(self):
        self.stage_template_cls = [
            IndexStage,
            QCStage,
            TophatStage,
            # CufflinkStage
        ]
        self.static_root = _here / 'report' / 'static'
