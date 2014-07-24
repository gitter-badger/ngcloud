from pathlib import Path
import ngcloud as ng
from ngcloud.report import Stage, Report
from ngcloud.util import copy, discover_file_by_patterns

logger = ng._create_logger(__name__)
_here = Path(__file__).parent


class IndexStage(Stage):
    template_name = 'index'
    template_root = _here / 'report' / 'templates'

class QCStage(Stage):
    template_name = 'qc'
    template_root = _here / 'report' / 'templates'

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
            # CufflinkStage,
        ]
        self.static_root = _here / 'report' / 'static'
