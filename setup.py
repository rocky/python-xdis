#!/usr/bin/env python
"""Setup script for the 'xdis' distribution."""

from __pkginfo__ import \
    author,           author_email,       entry_points, \
    license,          long_description,   classifiers,               \
    modname,          packages,           py_modules,         \
    scripts,          short_desc,         tests_require,             \
    VERSION,          web,                zip_safe

setup(
       author             = author,
       author_email       = author_email,
       classifiers        = classifiers,
       description        = short_desc,
       entry_points       = entry_points,
       license            = license,
       long_description   = long_description,
       long_description_content_type = "text/x-rst",
       name               = modname,
       packages           = packages,
       py_modules         = py_modules,
       # setup_requires     = setup_requires,
       tests_require      = tests_require,
       url                = web,
       version            = VERSION,
       zip_safe           = zip_safe)
