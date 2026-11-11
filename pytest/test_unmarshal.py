"""Lossless Python 2 interned strings and context-sensitive references."""

import io
from struct import pack

import pytest
from xdis.load import load_module_from_file_object
from xdis.magics import by_version, magic2int
from xdis.marsh import dumps
from xdis.unmarshal import VersionIndependentUnmarshaller, load_code


def string_record(tag, value):
    size = bytes([len(value)]) if tag == b"Z" else pack("<i", len(value))
    return tag + size + value


def reader(data, version="2.7"):
    return VersionIndependentUnmarshaller(
        io.BytesIO(data), magic2int(by_version[version]), False, code_objects={}
    )


def test_python2_interned_tuple_from_cpython():
    # CPython 2.7.18: value = intern('\xffA\x80'); marshal.dumps((value, value), 2)
    data = bytes.fromhex("28020000007403000000ff41805200000000")
    result = reader(data).r_object(bytes_for_s=True)
    assert result == (b"\xffA\x80", b"\xffA\x80")
    assert result[0] is result[1]
