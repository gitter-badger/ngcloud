from pathlib import Path
import ngcloud as ng
from ngcloud.report import Stage, Report
from ngcloud.util import copy, discover_file_by_patterns
from ngcloud.pipe import (
    _get_builtin_template_root,
    get_shared_template_root, get_shared_static_root
)

logger = ng._create_logger(__name__)
_here = Path(__file__).parent
_find_paths = [
    get_shared_template_root(),
    _get_builtin_template_root() / 'tuxedo',
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

    def copy_static(self):
        """Copy needed file for report in QC stage.

        - qc summary img *(not implemented)*
        - qc img by sample

        """
        self.copy_static_summary()
        self.copy_static_sample()

    def copy_static_summary(self):
        """Copy QC summary pics to static/qc_overall"""

        file_patterns = [
            'per_base_quality.png',
            'per_base_sequence_content.png',
        ]
        dest_root = self.report_root / 'static' / 'qc_overall'
        src_root = self.job_info.root_path / '1_fastqc' / 'overall'

        if not dest_root.exists():
            dest_root.mkdir(parents=True)

        for fp in file_patterns:
            copy(src_root / fp, dest_root)

    def copy_static_sample(self):
        """Copy QC sample pics to static/qc_sample/<sample_name>"""
        file_patterns = ['*.png']

        all_src_root = self.job_info.root_path / '1_fastqc' / 'output'
        all_dest_root = self.report_root / 'static' / 'qc_sample'

        for sample in self.job_info.sample_list:
            sp_src_root = (
                all_src_root / "{}_fastqc".format(sample.name) / "Images"
            )
            sp_dest_root = all_dest_root / sample.full_name / "pics"
            sp_dest_root.mkdir(parents=True)
            file_list = discover_file_by_patterns(sp_src_root, file_patterns)
            for f in file_list:
                copy(f, sp_dest_root)


class TophatStage(TuxedoBaseStage):
    template_entrances = 'tophat.html'


class TuxedoReport(Report):
    """NGCloud report class of Tuxedo pipeline."""

    stage_classnames = [
        IndexStage, QCStage, TophatStage,  # CufflinkStage,
    ]
    static_roots = get_shared_static_root()
