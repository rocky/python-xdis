.PHONY: help clean compile prepare get_sources test 

SOURCE=./templates/source/
COMPILED=./templates/compiled/
SERIALIZED=./templates/serialized/

# usage
define helptext
Crossversion xdis test usage:
	help         : show this menu
	clean        : remove compiled and serialized files
	compile      : with each tox env, compile all sources in $(SOURCE) to $(COMPILED), then serialize with dis to $(SERIALIZED)
	prepare      : clean then compile
	get_sources  : symlink all .py files in ./ -> $(SOURCE)
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

#: with each tox env, compile all sources in ./templates/source/ to ./templates/compiled/, then serialize with dis to ./templates/serialized/
compile:
	tox -c ./tox_prepare.ini

#: clean then compile
prepare: clean compile

#: copy all .py files in ./ -> ./templates/source/
get_sources:
	cp -f *.py $(SOURCE)

#: prepare and run tests. with each tox env, serialize pyc's in ./templates/compiled/<version> with xdis, then check against corresponding dis serialized pyc in ./templates/serialized/<version>
test: get_sources prepare
	tox
