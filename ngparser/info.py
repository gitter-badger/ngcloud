import yaml
from pathlib import Path
from ngparser.util import (
    open, abspath, expanduser,
    _val_bool_or_none,
)
import re

class Sample:
    """Sample experiment run information.

    Parameters
    ----------
    name : string
    pair_end : 'R1', 'R2', False, or None
    stranded : bool or None

    Note
    ----
    If a sample is pair-end, say sample 5566 has read 1 and 2, then one should
    explicitly creates two Sample instances

        >>> [Sample(name='5566_%s' % pe, pair_end=true) for pe in ['R1', 'R2']]
        [Sample(name='5566_R1'), Sample(name='5566_R2')]

   """

    _STR_FORMAT = '\n'.join([
        "Sample {0.name}",
        "    pair_end: {0.pair_end}",
        "    stranded: {0.stranded}"
    ])

    def __init__(self, name, pair_end=None, stranded=None):
        self.name = name            # SRR332241

        # bool check
        _val_bool_or_none(pair_end, 'pair_end')
        _val_bool_or_none(stranded, 'stranded')

        self.pair_end = pair_end
        self.stranded = stranded

    def __repr__(self):
        return "Sample(name={0.name!r})".format(self)

    def __str__(self):
        return Sample._STR_FORMAT.format(self)


class JobInfo:
    """Store a job information.

    Attributes
    ----------
    id : str
    type : str
    sample_list : list
        Lists of :class:`Sample` in this job

    Parameters
    ----------
    root_path : path like object
    """

    _read_folder_name = re.compile(
        r"^job_(?P<id>\d+)_(?P<type>\w+)$"
    ).match

    def __init__(self, root_path):
        self.root_path = Path(abspath(expanduser(root_path)))

        folder_info = self._parse_job_folder_name()
        self.id = folder_info['id']
        self.type = folder_info['type']

        self._raw = self._read_yaml()
        self.sample_list = self._parse_sample_list()

    def _read_yaml(self):
        with open(self.root_path / "job_info.yaml") as f:
            return yaml.load(f)

    def _parse_job_folder_name(self):
        folder_match = JobInfo._read_folder_name(self.root_path.name)
        if not folder_match or not self.root_path.is_dir():
            raise ValueError(
                "Unreadable folder path: {:s}".format(self.root_path)
            )
        return folder_match.groupdict()

    def _parse_sample_list(self):
        sample_list = []

        for sample in self._raw['sample_list']:
            name, info = next(iter(sample.items()))  # now a dict with one key
            # TODO:if user input SRR5566_R1 but no R2, needs to check
            sample_list.append(Sample(name, **info))

        return sample_list

