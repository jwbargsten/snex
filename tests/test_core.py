from snex.core import Snippet

def test_Snippet():
    s = Snippet.from_raw_data({"a": "b", "name":"dummy"}, ["a", "b", "c"], origin="core.py")
    assert s.name == "dummy"
