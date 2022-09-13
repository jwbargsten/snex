from snex.core import Snippet
import snex.core as core


def test_Snippet():
    s = Snippet.from_raw_data(
        {"a": "b", "name": "dummy"}, [" head", "", "a", "b", "", "c", "", " tail"], origin="core.py"
    )
    assert s.name == "dummy"
    assert s.body == ["a", "b", "", "c"]
    assert s.head == "head"
    assert s.tail == "tail"


def test_Snippet_prefixed():
    s = Snippet.from_raw_data(
        {"a": "b", "name": "dummy"},
        ["head", "", "a", "b", "", "c", "", "tail"],
        origin="core.py",
        prefix="u ",
    )
    assert s.name == "dummy"
    assert s.body == ["u a", "u b", "u ", "u c"]


def test_render_snippet():
    tmpl = "```{{lang}}\n{{{snippet}}}\n```"
    rendered = core.render_snippet(tmpl, {"lang": "bf"}, ["a", "b", "", "c"])
    assert rendered == "```bf\na\nb\n\nc\n```"
