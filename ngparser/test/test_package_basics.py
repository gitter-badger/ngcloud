from nose.tools import ok_
import re
import ngparser as ngp

def test_version_validity():
    version_match = re.match(r"^\d+\.\d+\.\d+($|\.dev)", ngp.__version__)
    ok_(version_match,
        msg="Unexpected version number: %s" % ngp.__version__)
