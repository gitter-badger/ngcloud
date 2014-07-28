from pathlib import Path
import shutil
from ngcloud.report import gen_report
from ngcloud.util import strify_path
from ngcloud import _create_logger

logger = _create_logger(__name__)

def cleanup_output(output_root):
    if not output_root.exists():
        output_root.mkdir()
        return

    logger.info('Remove previous outputs under output')
    previous_output = [
        strify_path(p) for p in output_root.iterdir()
        if p.is_dir() and p.name.startswith('report_')
    ]
    logger.warn(
        'These ouput reports will be removed: %s' % ', '.join(previous_output)
    )
    for pre in previous_output:
        shutil.rmtree(pre)

if __name__ == '__main__':
    output_root = Path('output')
    cleanup_output(output_root)

    gen_report(
        pipe_report_cls='ngcloud.pipe.tuxedo.TuxedoReport',
        job_dir=Path("job_9527_tuxedo_minimal"),
        out_dir=output_root
    )


