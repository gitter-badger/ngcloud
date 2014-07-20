from nose.tools import ok_
import re
import ngcloud as ng

def test_version_validity():
    version_match = re.match(r"^\d+\.\d+\.\d+($|\.dev)", ng.__version__)
    ok_(version_match,
        msg="Unexpected version number: %s" % ng.__version__)
