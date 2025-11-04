.PHONY: help clean get_sources setup_pyenv compile prepare test 

SOURCE=./templates/source/
COMPILED=./templates/compiled/
SERIALIZED=./templates/serialized/

# usage
define helptext
Crossversion xdis test usage:
	help         : show this menu
	clean        : remove compiled and serialized files
	get_sources  : symlink all .py files in ./ -> $(SOURCE)
	setup_pyenv  : setup local pyenv versions to be used by tox
    setup_uv     : setup tox-uv to run tests with uv
	compile      : with each tox env, compile all sources in $(SOURCE) to $(COMPILED), then serialize with dis to $(SERIALIZED)
	prepare      : fully prepare test environment and compile test files
	test         : prepare and run tests. with each tox env, serialize pyc's in $(COMPILED)<version> with xdis, then check against corresponding serialized pyc in $(SERIALIZED)<version>
endef
export helptext

#: show help menu
help:
	@echo "$$helptext"

#: remove compiled and serialized files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete
	rm -rf $(COMPILED)/*
	rm -rf $(SERIALIZED)/*

#: copy all .py files in ./ -> ./templates/source/
get_sources:
	cp -f *.py $(SOURCE)

.python-version:
	tox --listenvs | xargs pyenv local
#: setup local pyenv versions to be used by tox
setup_pyenv: .python-version

#: setup tox-uv so tox can use uv
setup_uv:
	uv tool install tox --with tox-uv

#: with each tox env, compile all sources in ./templates/source/ to ./templates/compiled/, then serialize with dis to ./templates/serialized/
compile:
	tox p -c ./tox_prepare.ini

.prepare_msg:
	@echo Ensure you have pyenv or uv installed and ran corresponding target setup_pyenv or setup_uv

#: fully prepare tests
prepare: .prepare_msg clean get_sources compile

#: prepare and run tests. with each tox env, serialize pyc's in ./templates/compiled/<version> with xdis, then check against corresponding dis serialized pyc in ./templates/serialized/<version>
test: prepare
	tox r -c ./tox.ini
