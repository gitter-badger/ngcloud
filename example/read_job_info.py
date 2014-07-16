import yaml
from pathlib import Path
from pprint import pprint

JOB_PATH = Path("/Users/liang/Documents/biocloud_datasets/job_9527_tuxedo")

def open(path_like, *args, **kwargs):
    if isinstance(path_like, Path):
        return path_like.open(*args, **kwargs)
    else:
        return open(path_like, *args, **kwargs)

with open(JOB_PATH / "job_info.yaml") as f:
    job_info = yaml.load(f)

pprint(job_info)
