#!/usr/bin/env python
# emacs-mode: -*-python-*-
"""
test_pyenvlib -- uncompyle and verify Python libraries

Usage-Examples:

  test_pyenvlib.py --all		# disassemble all tests across all pyenv libraries
  test_pyenvlib.py --all --verify	# disassemble all tests and verify results
  test_pyenvlib.py --test		# disassemble only the testsuite
  test_pyenvlib.py --2.7.11 --verify	# disassemble and verify python lib 2.7.11

Adding own test-trees:

Step 1) Edit this file and add a new entry to 'test_options', eg.
          test_options['mylib'] = ('/usr/lib/mylib', PYOC, 'mylib')
Step 2: Run the test:
	  test_pyenvlib --mylib	  # disassemble 'mylib'
	  test_pyenvlib --mylib --verify # disassemble verify 'mylib'
"""

from pyxdis import main, PYTHON3
import os, time, shutil
from fnmatch import fnmatch

#----- configure this for your needs

TEST_VERSIONS=('2.4.6', '2.5.6',
               '2.6.9', '2.7.10', '2.7.11',
               '3.2.6', '3.3.5',  '3.4.2', '3.5.1')

target_base = '/tmp/py-dis/'
lib_prefix = os.path.join(os.environ['HOME'], '.pyenv/versions')

PYC = ('*.pyc', )
PYO = ('*.pyo', )
PYOC = ('*.pyc', '*.pyo')

#-----

test_options = {
    # name: (src_basedir, pattern, output_base_suffix)
    'test': ('./test', PYOC, 'test'),
    }

for vers in TEST_VERSIONS:
    short_vers = vers[:3]
    test_options[vers] = (os.path.join(lib_prefix, vers, 'lib', 'python'+short_vers),
                          PYC, 'python-lib'+short_vers)

def do_tests(src_dir, patterns, target_dir, start_with=None,
                 do_verify=False, max_files=800, verbose=False):

    def visitor(files, dirname, names):
        files.extend(
            [os.path.normpath(os.path.join(dirname, n))
                 for n in names
                    for pat in patterns
                        if fnmatch(n, pat)])

    files = []
    cwd = os.getcwd()
    os.chdir(src_dir)
    if PYTHON3:
        for root, dirname, names in os.walk(os.curdir):
            files.extend(
                [os.path.normpath(os.path.join(root, n))
                     for n in names
                        for pat in patterns
                            if fnmatch(n, pat)])
            pass
        pass
    else:
        os.path.walk(os.curdir, visitor, files)
    files.sort()

    if start_with:
        try:
            start_with = files.index(start_with)
            files = files[start_with:]
            print('>>> starting with file', files[0])
        except ValueError:
            pass

    if len(files) > max_files:
        files = [file for file in files if not 'site-packages' in file]
        files = [file for file in files if not 'test' in file]
        if len(files) > max_files:
            files = files[:max_files]

    output = open(os.devnull,"w")
    # output = sys.stdout
    print(time.ctime())
    for i, file in enumerate(files):
        if verbose:
            print(os.path.join(src_dir, file))
        main.disassemble_file(file, output)
        if i % 100 == 0 and i > 0:
            print("Processed %d files" % (i))
    print("Processed %d files, total" % i)
    print(time.ctime())
    os.chdir(cwd)

if __name__ == '__main__':
    import getopt, sys

    do_verify = False
    test_dirs = []
    start_with = None
    max_files = 800

    test_options_keys = list(test_options.keys())
    test_options_keys.sort()
    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['start-with=',
                                'max-files=',
                                'verify', 'all', ] \
                               + test_options_keys )
    for opt, val in opts:
        if opt == '--verify':
            do_verify = True
        elif opt == '--start-with':
            start_with = val
        elif opt == '--max-files':
            max_files = int(val)
        elif opt[2:] in test_options_keys:
            test_dirs.append(test_options[opt[2:]])
        elif opt == '--all':
            for val in test_options_keys:
                test_dirs.append(test_options[val])

    for src_dir, pattern, target_dir in test_dirs:
        if os.path.exists(src_dir):
            target_dir = os.path.join(target_base, target_dir)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=1)
            do_tests(src_dir, pattern, target_dir, start_with,
                         do_verify=do_verify,
                         max_files=max_files)
        else:
            print("### Path %s doesn't exist; skipping" % src_dir)
