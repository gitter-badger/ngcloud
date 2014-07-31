from pathlib import Path
from ngcloud.report import Stage, Report

here = Path(__file__).parent
template_root = here / "report" / "templates"

class IndexStage(Stage):
    template_find_paths = template_root
    template_entrances = "index.html"

class MyStage(Stage):
    template_find_paths = template_root
    template_entrances = "mystage.html"

    def parse(self):
        self.result_info['mapped_rate'] = "50%"

        # real way
        mapped_rate = "(Unknown)"
        summary_txt = self.job_info.root_path / "my_stage" / "summary.txt"
        with summary_txt.open() as summary:
            for line in summary:
                if line.startswith("Overall"):
                    mapped_rate = line.strip().split(': ')[-1]

        self.result_info['mapped_rate'] = mapped_rate

class MyReport(Report):
    stage_classnames = [IndexStage, MyStage]
    static_roots = here / "report" / "static"
