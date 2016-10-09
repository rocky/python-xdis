# Copyright (c) 2015-2016 by Rocky Bernstein
# Copyright (c) 2000 by hartmut Goebel <h.goebel@crazy-compilers.com>

import imp, marshal, os, py_compile, sys, tempfile
from struct import unpack

import xdis.unmarshal
from xdis import PYTHON3, PYTHON_VERSION
from xdis import magics
from xdis.dropbox.decrypt25 import fix_dropbox_pyc

def check_object_path(path):
    if path.endswith(".py"):
        try:
            import importlib
            return importlib.util.cache_from_source(path,
                                                    optimization='')
        except:
            try:
                import imp
                imp.cache_from_source(path, debug_override=False)
            except:
                pass
            pass
        basename = os.path.basename(path)[0:-3]
        if PYTHON3:
            spath = path
        else:
            spath = path.decode('utf-8')
        path = tempfile.mkstemp(prefix=basename + '-',
                                suffix='.pyc', text=False)[1]
        py_compile.compile(spath, cfile=path, doraise=True)

    if not path.endswith(".pyc") and not path.endswith(".pyo"):
        raise ValueError("path %s must point to a .py or .pyc file\n" %
                         path)
    return path

def is_pypy(magic_int):
    return magic_int in (62211+7, 3180+7)

def load_file(filename):
    """
    load a Python source file and compile it to byte-code
    _load_file(filename: string): code_object
    filename:	name of file containing Python source code
                (normally a .py)
    code_object: code_object compiled from this source code
    This function does NOT write any file!
    """
    fp = open(filename, 'rb')
    try:
        source = fp.read().decode('utf-8') + '\n'
    except UnicodeDecodeError:
        fp.seek(0)
        source = fp.read() + '\n'

    try:
        if PYTHON_VERSION < 2.6:
            co = compile(source, filename, 'exec')
        else:
            co = compile(source, filename, 'exec', dont_inherit=True)
    except SyntaxError:
        sys.stderr.write('>>Syntax error in %s\n' % filename)
        fp.close()
        raise
    fp.close()
    return co

def load_module(filename, code_objects={}, fast_load=False,
                get_code=True):
    """load a module without importing it.
    load_module(filename: string): version, magic_int, code_object

    filename:	name of file containing Python byte-code object
                (normally a .pyc)

    code_object: code_object from this file
    version: Python major/minor value e.g. 2.7. or 3.4
    magic_int: more specific than version. The actual byte code version of the
               code object

    Parsing the  code object takes a bit of parsing time, but
    sometimes all you want is the module info, time string, code size,
    python version, etc. For that, set get_code=False.
    """

    timestamp = 0
    fp = open(filename, 'rb')
    magic = fp.read(4)
    magic_int = magics.magic2int(magic)

    # For reasons I don't understand PyPy 3.2 stores a magic
    # of '0'...  The two values below are for Pyton 2.x and 3.x respectively
    if magic[0:1] in ['0', b'0']:
        magic = magics.int2magic(3180+7)

    try:
        version = float(magics.versions[magic][:3])
    except KeyError:
        if len(magic) >= 2:
            fp.close()
            raise ImportError("Unknown magic number %s in %s" %
                            (ord(magic[0])+256*ord(magic[1]), filename))
        else:
            fp.close()
            raise ImportError("Bad magic number: '%s'" % magic)

    if magic_int in (3361,):
        fp.close()
        raise ImportError("%s is interim Python %s (%d) bytecode which is not "
                          "supported.\nFinal released versions are supported." %
                          (filename, magics.versions[magic], magics.magic2int(magic)))
    elif magic_int == 62135:
        fp.seek(0)
        return fix_dropbox_pyc(fp)
    elif magic_int == 62215:
        fp.close()
        raise ImportError("%s is a dropbox hacked Python %s (bytecode %d).\nSee "
                          "https://github.com/kholia/dedrop"
                          "for how to decrypt." %
                          (filename, version, magics.magic2int(magic)))

    # print version
    ts = fp.read(4)
    timestamp = unpack("I", ts)[0]
    my_magic_int = magics.magic2int(imp.get_magic())
    magic_int = magics.magic2int(magic)

    # Note: a higher magic number doesn't necessarily mean a later
    # release.  At Python 3.0 the magic number decreased
    # significantly. Hence the range below. Also note inclusion of
    # the size info, occurred within a Python major/minor
    # release. Hence the test on the magic value rather than
    # PYTHON_VERSION, although PYTHON_VERSION would probably work.
    if 3200 <= magic_int < 20121:
       source_size = unpack("I", fp.read(4))[0] # size mod 2**32
    else:
       source_size = None

    if get_code:
        if my_magic_int == magic_int:
            bytecode = fp.read()
            co = marshal.loads(bytecode)
        elif fast_load:
            co = xdis.marsh.load(fp, magic_int, code_objects)
        else:
            co = xdis.unmarshal.load_code(fp, magic_int, code_objects)
        pass
    else:
        co = None

    fp.close()

    return version, timestamp, magic_int, co, is_pypy(magic_int), source_size

if __name__ == '__main__':
    co = load_file(__file__)
    obj_path = check_object_path(__file__)
    version, timestamp, magic_int, co2, pypy, source_size = load_module(obj_path)
    print("version", version, "magic int", magic_int, 'is_pypy', pypy)
    import datetime
    print(datetime.datetime.fromtimestamp(timestamp))
    if source_size:
        print("source size mod 2**32: %d" % source_size)
    if version < 3.5:
        assert co == co2
