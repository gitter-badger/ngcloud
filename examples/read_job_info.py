import sys
from pathlib import Path
from ngcloud.info import JobInfo

def main():
    if sys.platform == "darwin":
        JOB_PATH = Path("job_9527_tuxedo_minimal")
    elif sys.platform.startswith("linux"):
        JOB_PATH = Path("job_9527_tuxedo_minimal")

    job_info = JobInfo(JOB_PATH)

    print(job_info.id, job_info.type)

    sample_list = job_info.sample_list
    print(sample_list)
    for sample in sample_list:
        print(sample)

if __name__ == "__main__":
    main()

