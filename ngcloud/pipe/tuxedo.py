import re
from pathlib import Path
from collections import OrderedDict, namedtuple
import ngcloud as ng
from ngcloud.report import Stage, Report
from ngcloud.pipe import (
    _get_builtin_report_root,
    get_shared_template_root, get_shared_static_root
)
from ngcloud.util import open

logger = ng._create_logger(__name__)
_here = Path(__file__).parent
_find_paths = [
    _get_builtin_report_root() / 'tuxedo' / 'templates',
    get_shared_template_root(),
]

__doc__ = """\
Built-in report templates for Tuxedo pipeline.

Class created for the pipeline
------------------------------
.. autosummary::
    :nosignatures:

    TuxedoReport
    IndexStage
    QCStage
    TophatStage

Result folder structure
-----------------------

.. code::

    <Report.job_info.root_path>
    ├── fastqc/
    │   └── <sample.full_name>/     # Original FastQC result
    ├── tophat/
    │   └── <sample.name>/          # Original Tophat result
    ├── cufflinks/
    │   └── <sample.name>/          # Original Cufflinks result

Job info special attributes
---------------------------

.. code-block:: yaml

    # (skip common attibutes)
    pipe_parameters:
        tophat:
        cufflinks:

Miscellaneous:

- :class:`TuxedoBaseStage`
- :class:`OverSeq`

"""

# According to the threads on Tuxedo Tools User Group,
# We read the alignment status from aling_summary.txt
# https://groups.google.com/d/msg/tuxedo-tools-users/s_oQRTwCuXA/_0PL4thE8OYJ
_align_txt_left = (
    r"Left reads:\n"
    r"\s*Input\s*:\s*(?P<left_input>\d+)\n"
    r"\s*Mapped\s*:\s*(?P<left_map>\d+) \([ 0-9.%]* of input\)\n"
    r"\s*of these:\s*(?P<left_multimap>\d+) \([ 0-9.%]*\) "
    r"have multiple alignments \((?P<left_multicount>\d+) have >1\)\n"
)
_align_txt_right = _align_txt_left.replace(
    'Left', 'Right').replace('left', 'right')
_align_txt_aligned = (
    r"\s*Aligned pairs:\s*(?P<align_pair>\d+)\n"
    r"\s*of these:\s*(?P<align_multi>\d+) \([ 0-9.%]*\) .*\n"
    r"\s*(?P<align_discord>\d+) \([ 0-9.%]*\) are discordant alignments\n"
)
_extract_separate = re.compile(
    _align_txt_left + _align_txt_right, re.MULTILINE
).search
_extract_align = re.compile(
    _align_txt_aligned, re.MULTILINE
).search

OverSeq = namedtuple(
    "OverSeq", ["seq", "count", "percentage", "possible_source"])

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
    """Index page for Tuxedo pipeline"""
    template_entrances = 'index.html'


class QCStage(TuxedoBaseStage):
    """QC page for Tuxedo pipeline from output of FastQC"""
    template_entrances = 'qc.html'
    result_foldername = 'fastqc'
    # embed_result_joint = [
    #     {'src': 'overall',
    #      'patterns': [
    #          'per_base_quality.png',
    #          'per_base_sequence_content.png'
    #      ],
    #      'dest': 'qc_overall'},
    # ]
    embed_result_persample = [
        {'src': '',
         'patterns': ['Images/*.png'],
         'dest': 'qc_sample/pics'},
    ]
    FASTQC_FILENAME = {
        'Per base sequence quality': 'per_base_quality.png',
        'Per sequence quality scores': 'per_sequence_quality.png',
        'Per base sequence content': 'per_base_sequence_content.png',
        'Per base GC content': 'per_base_gc_content.png',
        'Per sequence GC content': 'per_sequence_gc_content.png',
        'Per base N content': 'per_base_n_content.png',
        'Sequence Length Distribution': 'sequence_length_distribution.png',
        'Sequence Duplication Levels': 'duplication_levels.png',
    }
    FASTQC_NOFILE = [
        'Basic Statistics',
        'Overrepresented sequences',
        'Kmer Content'
    ]
    FASTQC_GLYPH = {
        'pass': 'glyphicon-ok',
        'warn': 'glyphicon-exclamation-sign',
        'fail': 'glyphicon-remove'
    }

    def read_fastqc_data(self, sample):
        qc_info = OrderedDict()
        over_seq = []
        qc_desc = None
        qc_data_pth = self.result_root / sample.full_name / 'fastqc_data.txt'
        with open(qc_data_pth) as qc_data:
            # parse FASTQC by brute force
            for line in qc_data:
                new_sec = line.startswith('>>')
                sec_end = line.startswith('>>END_MODULE')
                if new_sec and not sec_end:
                    qc_desc, qc_status = line.rstrip()[2:].rsplit('\t', 1)
                    qc_info[qc_desc] = qc_status
                    if qc_desc == "Overrepresented sequences":
                        next_line = next(qc_data)
                        while not sec_end:
                            if not next_line.startswith("#Seq"):
                                over_seq.append(
                                    OverSeq(*next_line.rstrip().split('\t'))
                                )
                            next_line = next(qc_data)
                            sec_end = next_line.startswith('>>END_MODULE')
        return qc_info, over_seq

    def parse(self):
        super().parse()
        self.result_info['qc_info'] = dict()
        self.result_info['over_seq'] = dict()
        for sample in self.job_info.sample_list:
            qc_info, over_seq = self.read_fastqc_data(sample)
            self.result_info['qc_info'][sample.full_name] = qc_info
            self.result_info['over_seq'][sample.full_name] = over_seq
        self.result_info.update({
            "FASTQC_FILENAME": self.FASTQC_FILENAME,
            "FASTQC_NOFILE": self.FASTQC_NOFILE,
            "FASTQC_GLYPH": self.FASTQC_GLYPH
        })


class TophatStage(TuxedoBaseStage):
    """Tophat stage for Tuxedo pipeline"""
    result_foldername = 'tophat'
    template_entrances = 'tophat.html'

    DETAIL_SEP = [
        ('Input', 'input'),
        ('Mapped', 'map'),
        ('Multi', 'multimap'),
        ('Multi Count', 'multicount')
    ]
    DETAIL_PAIR = [
        ('Aligned pairs', 'pair'),
        ('Mutli-align pairs', 'multi'),
        ('Discordants pairs', 'discord')
    ]

    def parse(self):
        super().parse()
        self.set_const()
        self.result_info['detail_info'] = dict()
        for group, sample_list in self.job_info.sample_group.items():
            detail_info = self.parse_sample(group, sample_list)
            self.result_info['detail_info'][group] = detail_info

    def set_const(self):
        for const in ['DETAIL_SEP', 'DETAIL_PAIR']:
            self.result_info[const] = getattr(TophatStage, const)

    def parse_sample(self, group, sample_list):
        logger.debug("Reading align_summary.txt")
        align_txt = self.result_root / group / 'align_summary.txt'
        with open(align_txt) as align_summary:
            raw_string = align_summary.read()

        match_sep = _extract_separate(raw_string)
        if not match_sep:
            raise ValueError("Cannot get left/right info in align_summary.txt")
        match_align = _extract_align(raw_string)
        if not match_align:
            raise ValueError("Cannot get pair info in align_summary.txt")

        info_dict = {
            k: int(v)
            for m in [match_sep, match_align]
            for k, v in m.groupdict().items()
        }
        return info_dict

class TuxedoReport(Report):
    """NGCloud report class of Tuxedo pipeline."""

    stage_classnames = [
        IndexStage, QCStage, TophatStage,  # CufflinkStage,
    ]
    static_roots = [
        get_shared_static_root(),
        _get_builtin_report_root() / 'tuxedo' / 'static',
    ]
