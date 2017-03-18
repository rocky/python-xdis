PHONY=check test pytest clean

PYTHON ?= python

#: Whatever you need to do, do it in ..
test check test-unit:
	$(MAKE) -C .. $@

clean:
	rm -fr __pycache__ || true
