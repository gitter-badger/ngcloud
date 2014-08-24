import re
import logging
# TODO: 3.3 compatiblity
import statistics as stats
from pathlib import Path
from ngcloud.report import SummaryStage, main as _main
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
    def parse(self):
        super().parse()
        logger.debug('Get overall pair align rate')
        self.compute_overall()

    def compute_overall(self):
        detail = self.result_info['detail_info']
        sep_rate = dict()
        pair_rate = dict()
        for group in self.sample_group:
            left_all = detail[group]['left_input']
            right_all = detail[group]['right_input']
            if not left_all == right_all:
                raise ValueError(
                    "Unequal numbers of read for pair-end sample"
                    "{}".format(group))
            sep_rate[group] = [
                detail[group][d + '_map'] / left_all
                for d in ['left', 'right']
            ]
            pair_rate[group] = detail[group]['align_pair'] / left_all

        self.result_info['sep_rate'] = sep_rate
        self.result_info['pair_rate'] = pair_rate
        self.result_info['overall_sep_rate'] = stats.mean(
            rate
            for group_rates in sep_rate.values()
            for rate in group_rates
        )
        self.result_info['overall_pair_rate'] = stats.mean(
            rate for rate in pair_rate.values()
        )

class IndexStage(SummaryStage, TuxedoBaseStage, tuxedo.IndexStage):
    pass

class CufflinksStage(TuxedoBaseStage):
    """Cufflinks stage for Tuxedo pipeline"""
    result_foldername = 'cufflinks'
    template_entrances = 'cufflinks.html'

    def set_const(self):
        pass

    def parse(self):
        super().parse()
        self.set_const()
        for group, sample_list in self.sample_group.items():
            pass

class TuxedoReport(tuxedo.TuxedoReport):
    stage_classnames = [
        IndexStage, tuxedo.QCStage, TophatStage, CufflinksStage
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
