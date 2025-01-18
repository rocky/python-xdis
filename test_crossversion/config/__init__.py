from configparser import ConfigParser
from pathlib import Path
from sys import version_info

# main test root dir
_test_path = Path(__file__).parent.parent

# system version of python
SYS_VERSION = f"{version_info.major}.{version_info.minor}"

# template dirs
TEMPLATE_DIR = _test_path / "templates"
TEMPLATE_SOURCE_DIR = TEMPLATE_DIR / "source"
TEMPLATE_COMPILED_DIR = TEMPLATE_DIR / "compiled"
TEMPLATE_SERIALIZED_DIR = TEMPLATE_DIR / "serialized"

# check dirs and make them if needed
_check_dir = lambda dir: dir.mkdir() if not dir.exists() else True
_check_dir(TEMPLATE_DIR)
_check_dir(TEMPLATE_SOURCE_DIR)
_check_dir(TEMPLATE_COMPILED_DIR)
_check_dir(TEMPLATE_SERIALIZED_DIR)
