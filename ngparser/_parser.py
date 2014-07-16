from pathlib import Path

class NGSSample:
    def __init__(self, name, pair_end):
        self.name = name            # SRR332241
        self.pair_end = pair_end


class StageResult:
    def __init__(self, root_path, sample_list):
        self.sample_list = []
        if not isinstance(root_path, Path):
            self.root_path = Path(root_path)
        else:
            self.root_path = root_path

    def all_samples(self):
        for sample in self.sample_list:
            if sample.pair_end:
                yield "%s_R1" % sample.name
                yield "%s_R2" % sample.name
            else:
                yield "%s"
