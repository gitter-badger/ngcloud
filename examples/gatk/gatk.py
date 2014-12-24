from pathlib import Path
from ngcloud import _create_logger
from ngcloud.report import Stage, Report
from ngcloud.pipe import get_shared_template_root, get_shared_static_root
from ngcloud.pipe import tuxedo
from ngcloud.util import open

logger = _create_logger(__name__)
_here = Path(__file__).parent

class GATKBaseStage(Stage):
    template_find_paths = [
        _here / "report" / "templates",
        get_shared_template_root(),
    ]

class IndexStage(GATKBaseStage):
    template_entrances = 'index.html'

class QCStage(tuxedo.QCStage):
    # template_find_paths = GATKBaseStage.template_find_paths
    # template_find_paths.append(
    #     _get_builtin_template_root() / 'tuxedo'
    # )
    template_find_paths = (
        GATKBaseStage.template_find_paths[:1] +
        tuxedo.QCStage.template_find_paths
    )

class AlignStage(GATKBaseStage):
    template_entrances = 'align.html'


class VCFStage(GATKBaseStage):
    # transform vcf into html table 
    def vcf2html(self, vcffile):
        vcfile_path = self.result_root / 'gatk' 
        output_html_path = _here / 'report' / 'templates' / 'tables' / str(vcffile + '.html')

        with open(vcfile_path / vcffile) as vcf:
            start_flag = 0 
            output = open(output_html_path,'w')

            print('<table id="example" class="table" cellspacing="0" width="100%" style="word-break:break-all">', file = output)
            # table head
            for line in vcf:    
                if line.startswith("#CHROM") == True:
                    start_flag = 1
                    if start_flag == 1:
                        print('<thead>' + '\n' + '\t' + '<tr>', file = output)
                        col = line.strip().split("\t")
                        for i in col[0:7]:
                            print('\t\t' + '<td width = "14.28%">'+i+'</td>', file = output)
                        break
            print('\t' + '</tr>' + '\n'+ '</thead>' + '\n', file = output)

            # table body
            print('<tbody>' + '\n', file = output)
            for line in vcf:
                print('\t' + '<tr>', file = output)
                col = line.strip().split("\t")
                for i in col[0:7]:
                    print('\t\t' + '<td>' + i + '</td>', file = output)        
                print('\t' + '</tr>', file = output)
            print('</tbody>'+ '\n' + '</table>', file = output)

    def parse(self):
         self.vcf2html('gatk_result.vcf')
        
class GATKStage(GATKBaseStage):
    template_entrances = 'gatk.html'

class GATKReport(Report):
    stage_classnames = [
        IndexStage, QCStage, AlignStage, VCFStage, GATKStage
    ]
    static_roots = [
        _here / 'report' / 'static',
        get_shared_static_root(),
    ]
