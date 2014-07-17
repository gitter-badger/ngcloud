import sys
from os.path import expanduser
from pathlib import Path
from ngparser.info import JobInfo

def main():
    if sys.platform == "darwin":
        JOB_PATH = Path(
            expanduser("~/Documents/biocloud_datasets/job_9527_tuxedo"))
    elif sys.platform.startswith("linux"):
        JOB_PATH = Path(
            expanduser("~/dataset/biocloud/job_9527_tuxedo"))

    job_info = JobInfo(JOB_PATH)

    print(job_info.id, job_info.type)

    sample_list = job_info.sample_list
    print(sample_list)
    for sample in sample_list:
        print(sample)

if __name__ == "__main__":
    main()

