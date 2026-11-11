"""Python 2 Unicode literal representations on Python 3 hosts."""

import ast
import io
from struct import pack

import pytest
from xdis.cross_types import UnicodeForPython3
from xdis.magics import by_version, magic2int
from xdis.unmarshal import VersionIndependentUnmarshaller

# Also verified by parsing and re-marshalling with stock CPython 2.7.18.
UNICODE_REPR_CASES = (
    ("", "u''"),
    ("plain ASCII", "u'plain ASCII'"),
    ("\u4e00\u6b21\u6700\u591a", r"u'\u4e00\u6b21\u6700\u591a'"),
    ("abc\u4e2d\u6587", r"u'abc\u4e2d\u6587'"),
    ("\u4e2d", r"u'\u4e2d'"),
    ("\u00e9", r"u'\xe9'"),
    ("\u0100", r"u'\u0100'"),
    ("\U0001f600", r"u'\U0001f600'"),
    ("\U0010ffff", r"u'\U0010ffff'"),
    ("it's", 'u"it\'s"'),
    ('say "hi"', """u'say "hi"'"""),
    ("both ' and \"", "u'both \\' and \"'"),
    ("back\\slash", r"u'back\\slash'"),
    ("\\u4e2d", r"u'\\u4e2d'"),
    ("line\nbreak", r"u'line\nbreak'"),
    ("carriage\rreturn", r"u'carriage\rreturn'"),
    ("nul\0tab\t", r"u'nul\x00tab\t'"),
    ("\x01\x1f\x7f", r"u'\x01\x1f\x7f'"),
    ("e\u0301", r"u'e\u0301'"),
    ("\u2028\u2029", r"u'\u2028\u2029'"),
    ("\u4e2d'\\\n", r'''u"\u4e2d'\\\n"'''),
)


@pytest.mark.parametrize("text, expected", UNICODE_REPR_CASES)
def test_python2_unicode_repr_roundtrip(text, expected):
    raw = text.encode("utf-8")
    value = UnicodeForPython3(raw)
    literal = repr(value)
    assert literal == expected
    assert literal.isascii()
    assert ast.literal_eval(literal) == text
    assert str(value) == text
    assert value.value == raw


@pytest.mark.parametrize("version", ("2.7", "3.3"))
@pytest.mark.parametrize(
    "text", ("\u4e00\u6b21\u6700\u591a", "abc\u4e2d\u6587", "\u4e2d")
)
def test_marshaled_unicode_repr_roundtrip(version, text):
    raw = text.encode("utf-8")
    data = b"u" + pack("<i", len(raw)) + raw
    reader = VersionIndependentUnmarshaller(
        io.BytesIO(data), magic2int(by_version[version]), False, code_objects={}
    )
    value = reader.load()
    if version == "2.7":
        assert isinstance(value, UnicodeForPython3)
        assert value.value == raw
        assert repr(value).startswith("u")
    else:
        assert type(value) is str
    assert ast.literal_eval(repr(value)) == text
