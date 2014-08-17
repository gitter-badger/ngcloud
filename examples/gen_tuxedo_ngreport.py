from pathlib import Path
import logging
from ngcloud.report import gen_report

if __name__ == '__main__':
    output_root = Path('output')
    if not output_root.exists():
        output_root.mkdir()

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "[%(levelname)s][%(name)s] %(message)s"))
    ng_loggers = logging.getLogger("ngcloud")
    ng_loggers.addHandler(console)
    ng_loggers.setLevel(logging.INFO)

    gen_report(
        pipe_report_cls='ngcloud.pipe.tuxedo.TuxedoReport',
        job_dir=Path("job_tuxedo_minimal"),
        out_dir=output_root
    )


