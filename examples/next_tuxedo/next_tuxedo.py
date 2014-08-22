import re
import logging
from pathlib import Path
from ngcloud.report import main as _main
from ngcloud.pipe import tuxedo
from ngcloud.util import open

logger = logging.getLogger("external.%s" % __name__)

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

class TophatStage(tuxedo.TophatStage):
    result_foldername = 'tophat'
    template_find_paths = tuxedo.TuxedoBaseStage.template_find_paths[:]
    template_find_paths.insert(0, Path('templates'))

    DETAIL_SEP = [
        ('Input', 'input'),
        ('Mapped', 'map'),
        ('Multi', 'multimap'),
        ('Multi Count', 'multicount')
    ]

    def parse(self):
        super().parse()
        self.result_info['detail_info'] = dict()
        self.result_info['DETAIL_SEP'] = TophatStage.DETAIL_SEP
        for group, sample_list in self.job_info.sample_group.items():
            detail_info = self.parse_sample(group, sample_list)
            self.result_info['detail_info'][group] = detail_info

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
