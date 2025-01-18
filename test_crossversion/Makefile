.PHONY: clean compile prepare test get_sources

SOURCE=./templates/source/
COMPILED=./templates/compiled/
SERIALIZED=./templates/serialized/

# usage
define helptext
Crossversion xdis test usage:
	help | usage : show this menu
	clean        : remove compiled and serialized files
	compile      : with each tox env, compile all sources in $(SOURCE) to $(COMPILED), then serialize with dis to $(SERIALIZED)
	prepare      : clean then compile
	get_sources  : symlink all .py files in ./ -> $(SOURCE)
	test         : prepare and run tests. with each tox env, serialize pyc's in $(COMPILED)<version> with xdis, then check against corresponding serialized pyc in $(SERIALIZED)<version>
endef
export helptext

help:
	@echo "$$helptext"

usage: help

# clean compiled files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete
	rm -rf $(COMPILED)/*
	rm -rf $(SERIALIZED)/*

# compile sources in templates/source
compile:
	tox -c ./tox_prepare.ini

prepare: clean compile

# sim link python source files to ./templates/source
get_sources:
	cp -f *.py $(SOURCE)

# main test
test: get_sources prepare
	tox
