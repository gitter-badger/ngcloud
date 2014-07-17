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
    pair_end : bool or None
    stranded : bool or None
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
        self._root = Path(expanduser(root_path))

        folder_info = self._parse_job_folder()
        self.id = folder_info['id']
        self.type = folder_info['type']

        self._raw = self._read_yaml()
        self.sample_list = self._parse_sample_list()
        self.expanded_sample_list = list(self._expand_sample_list())

    def _expand_sample_list(self):
        """Yield full name list of all samples.

        Pair-end samples will be expressed as sample_R1, sample_R2.

        Return
        ------
        Generator of list of sample names, R1 and R2 are seperated.
        """
        for sample in self.sample_list:
            if sample.pair_end:
                yield "%s_R1" % sample.name
                yield "%s_R2" % sample.name
            else:
                yield "%s" % sample.name

    def _read_yaml(self):
        with open(self._root / "job_info.yaml") as f:
            return yaml.load(f)

    def _parse_job_folder(self):
        folder_match = JobInfo._read_folder_name(self._root.name)
        if not folder_match or not self._root.is_dir():
            raise ValueError(
                "Unreadable folder path: {:s}".format(abspath(self._root))
            )
        return folder_match.groupdict()

    def _parse_sample_list(self):
        sample_list = []

        for sample in self._raw['sample_list']:
            name, info = next(iter(sample.items()))  # now a dict with one key
            sample_list.append(Sample(name, **info))

        return sample_list

