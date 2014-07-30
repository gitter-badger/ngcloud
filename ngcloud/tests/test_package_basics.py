from nose.tools import ok_
import ngcloud as ng

def test_version_validity():
    ok_(ng.__version__, msg="Version number not found!")
