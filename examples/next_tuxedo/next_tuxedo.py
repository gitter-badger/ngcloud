import re
import logging
from pathlib import Path
from ngcloud.report import main as _main
from ngcloud.pipe import tuxedo
from ngcloud.util import open  # flake8: noqa

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
    template_find_paths = tuxedo.TuxedoBaseStage.template_find_paths[:]
    template_find_paths.insert(0, Path('templates'))

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
