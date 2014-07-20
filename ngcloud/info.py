import yaml
from pathlib import Path
from ngcloud.util import (
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


    Attributes
    ----------
    name : string
        Sample name. Pair-end samples should have same ``name``

    full_name : string
        Auto-generated full sample name, containing pair-end info.
        So pair-end samples should have different ``full_name``


    Examples
    --------
    If a sample is pair-end, say sample 5566 has read 1 and 2, then one should
    explicitly creates two Sample instances

        >>> pe = [Sample(name='5566' % pe, pair_end=pe) for pe in ['R1', 'R2']]
        >>> pe
        [Sample(name='5566'), Sample(name='5566')]
        >>> print(pe[0])  # get first pair-end sample
        Sample 5566
            pair_end: R1
            stranded: None

        >>> pe[0].full_name
        '5566_R1'

   """

    _STR_FORMAT = '\n'.join([
        "Sample {0.name}",
        "    pair_end: {0.pair_end}",
        "    stranded: {0.stranded}"
    ])

    def __init__(self, name, pair_end=None, stranded=None):
        self.name = name            # SRR332241

        # bool check
        Sample._val_pair_end(pair_end)
        _val_bool_or_none(stranded, 'stranded')

        self.pair_end = pair_end
        self.stranded = stranded

        self.full_name = self._gen_full_name()

    def __repr__(self):
        return "Sample(name={0.name!r})".format(self)

    def __str__(self):
        return Sample._STR_FORMAT.format(self)

    def _gen_full_name(self):
        if self.pair_end:
            return "{0.name}_{0.pair_end}".format(self)
        else:
            return self.name

    @staticmethod
    def _val_pair_end(pair_end):
        if pair_end not in ['R1', 'R2', False, None]:
            raise ValueError(
                "Unexpected pair-end type: {}".format(pair_end)
            )


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

