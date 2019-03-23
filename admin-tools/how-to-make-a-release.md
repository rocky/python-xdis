<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Get latest sources:](#get-latest-sources)
- [Change version in xdis/version.py.](#change-version-in-xdisversionpy)
- [Update ChangeLog:](#update-changelog)
- [Update NEWS from ChangeLog. Then:](#update-news-from-changelog-then)
- [Make sure pyenv is running and check newer versions](#make-sure-pyenv-is-running-and-check-newer-versions)
- [Switch to python-2.4, sync that up and build that first since it creates a tarball which we don't want.](#switch-to-python-24-sync-that-up-and-build-that-first-since-it-creates-a-tarball-which-we-dont-want)
- [Update NEWS from master branch](#update-news-from-master-branch)
- [Check against all versions](#check-against-all-versions)
- [Make packages and tag](#make-packages-and-tag)
- [Upload single package and look at Rst Formating](#upload-single-package-and-look-at-rst-formating)
- [Upload rest of versions](#upload-rest-of-versions)
- [Push tags:](#push-tags)
- [Check on a VM](#check-on-a-vm)

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

#  Update NEWS from ChangeLog. Then:

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

# Update NEWS from master branch

    $ git commit -m"Get ready for release $VERSION" .

# Check against all versions

    $ bash && echo $SHLVL # Go into a subshell to protect exit
    $ source admin-tools/check-older-versions.sh
    $ source admin-tools/check-newer-versions.sh
    $ echo $SHLVL ; exit

# Make packages and tag

    $ . ./admin-tools/make-dist-older.sh
    $ git tag release-python-2.4-$VERSION

    $ . ./admin-tools/make-dist-newer.sh

Goto https://github.com/rocky/python-xdis/releases



# Upload single package and look at Rst Formating

    $ twine upload dist/xdis-${VERSION}-py3.3.egg

Check on https://pypi.org/project/xdis/

# Upload rest of versions

    $ twine upload dist/xdis-${VERSION}*

# Push tags:

    $ git push --tags

# Check on a VM

    $ cd /virtual/vagrant/virtual/vagrant/ubuntu-zesty
	$ vagrant up
	$ vagrant ssh
	$ pyenv local 3.5.2
	$ pip install --upgrade xdis
	$ exit
	$ vagrant halt
