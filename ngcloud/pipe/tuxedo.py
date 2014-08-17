from pathlib import Path
import ngcloud as ng
from ngcloud.report import Stage, Report
from ngcloud.pipe import (
    _get_builtin_template_root,
    get_shared_template_root, get_shared_static_root
)

logger = ng._create_logger(__name__)
_here = Path(__file__).parent
_find_paths = [
    _get_builtin_template_root() / 'tuxedo',
    get_shared_template_root(),
]


class TuxedoBaseStage(Stage):
    template_find_paths = _find_paths

    def parse(self):
        self.result_info['stage_mapping'] = [
            ('summary', 'index.html', 'Summary'),
            ('qc', 'qc.html', 'Quality Control'),
            ('tophat', 'tophat.html', 'Alignment'),
            ('cufflinks', 'cufflinks.html', 'Expression Quantification'),
        ]

class IndexStage(TuxedoBaseStage):
    template_entrances = 'index.html'


class QCStage(TuxedoBaseStage):
    template_entrances = 'qc.html'
    result_foldername = 'fastqc'
    embed_result_joint = [
        {'src': 'overall',
         'patterns': ['per_base_quality.png', 'per_base_sequence_content.png'],
         'dest': 'qc_overall'},
    ]
    embed_result_persample = [
        {'src': 'output',
         'patterns': ['Images/*.png'],
         'dest': 'qc_sample/pics'},
    ]


class TophatStage(TuxedoBaseStage):
    template_entrances = 'tophat.html'


class TuxedoReport(Report):
    """NGCloud report class of Tuxedo pipeline."""

    stage_classnames = [
        IndexStage, QCStage, TophatStage,  # CufflinkStage,
    ]
    static_roots = get_shared_static_root()
