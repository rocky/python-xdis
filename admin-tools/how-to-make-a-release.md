<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in xdis/version.py.](#change-version-in-xdisversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS.md from ChangeLog. Then:](#update-newsmd-from-changelog-then)
- [Make sure pyenv is running and check newer versions](#make-sure-pyenv-is-running-and-check-newer-versions)
- [Switch to python-2.4, sync that up and build that first since it creates a tarball which we don't want.](#switch-to-python-24-sync-that-up-and-build-that-first-since-it-creates-a-tarball-which-we-dont-want)
- [Update NEWS.md from master branch](#update-newsmd-from-master-branch)
- [Check against all versions](#check-against-all-versions)
- [Make packages and tag](#make-packages-and-tag)
- [Check package on github](#check-package-on-github)
- [Release on Github](#release-on-github)
- [Get on PyPI](#get-on-pypi)
- [Push tags:](#push-tags)
- [Move dist files to uploaded](#move-dist-files-to-uploaded)

<!-- markdown-toc end -->

# Get latest sources:

    $ git pull

# Change version in xdis/version.py.

    $ emacs xdis/version.py
    $ source xdis/version.py
    $ echo $VERSION
    $ git commit -m"Get ready for release $VERSION" .


# Update ChangeLog:

    $ make ChangeLog

#  Update NEWS.md from ChangeLog. Then:

    $ emacs NEWS.md
    $ make check
    $ git commit --amend .
    $ git push   # get CI testing going early
    $ make check-full

# Make sure pyenv is running and check newer versions

    $ pyenv local && source admin-tools/check-newer-versions.sh

# Switch to python-2.4, sync that up and build that first since it creates a tarball which we don't want.

    $ source admin-tools/setup-python-2.4.sh
    $ git merge master

# Update NEWS.md from master branch

    $ git commit -m"Get ready for release $VERSION" .

# Check against all versions

    $ bash && echo $SHLVL # Go into a subshell to protect exit
    $ source admin-tools/check-older-versions.sh
    $ echo $SHLVL ; exit

# Make packages and tag

    $ . ./admin-tools/make-dist-older.sh
	$ pyenv local 3.8.3
	$ twine check dist/xdis-$VERSION*
    $ git tag release-python-2.4-$VERSION
    $ . ./admin-tools/make-dist-newer.sh
	$ twine check dist/xdis-$VERSION*

# Check package on github

	$ mkdir /tmp/gittest; pushd /tmp/gittest
	$ pyenv local 3.7.5
	$ pip install -e git://github.com/rocky/python-xdis.git#egg=xdis
	$ pydisasm --help
	$ pip uninstall xdis
	$ popd

# Release on Github

Goto https://github.com/rocky/python-xdis/releases/new

Now check the *tagged* release. (Checking the untagged release was previously done).

Todo: turn this into a script in `admin-tools`

	$ pushd /tmp/gittest
	$ pip install -e git://github.com/rocky/python-xdis@$VERSION.git#egg=xdis
	$ pydisasm --help
	$ pip uninstall xdis
	$ popd


# Get on PyPI

	$ twine upload dist/xdis-${VERSION}*

Check on https://pypi.org/project/xdis/

# Push tags:

    $ git push --tags
    $ git pull --tags

# Move dist files to uploaded

	$ mv -v dist/xdis-${VERSION}* dist/uploaded
