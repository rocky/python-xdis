import argparse
import logging
from py_compile import compile

from config import (
    SYS_VERSION,
    TEMPLATE_COMPILED_DIR,
    TEMPLATE_SERIALIZED_DIR,
    TEMPLATE_SOURCE_DIR,
)
from serialize_bytecode import serialize_pyc


def prepare_templates():
    """
    Compile files in template source dir, then serialize with dis
    Intermediary steps are saved in respective folders in templates / <compiled|serialized> / <version>
    """
    # create folders to save pyc's
    compiled_dir = TEMPLATE_COMPILED_DIR / SYS_VERSION
    serialized_dir = TEMPLATE_SERIALIZED_DIR / SYS_VERSION
    if not compiled_dir.exists():
        compiled_dir.mkdir()
    if not serialized_dir.exists():
        serialized_dir.mkdir()

    # compile and serialize template files
    num_source = 0
    for source in TEMPLATE_SOURCE_DIR.glob("*.py"):
        # create paths
        pyc_file = compiled_dir / f"{source.stem}_{SYS_VERSION}.pyc"
        serialized_file = serialized_dir / f"{source.stem}_{SYS_VERSION}.txt"

        # compile pyc
        compile(str(source), str(pyc_file))
        logging.info(f"Compiled {str(source)} -> {str(pyc_file)}")

        # serialize pyc
        with serialized_file.open("w") as f:
            serialize_pyc(pyc_file, False, f)
        logging.info(f"Serialized {str(pyc_file)} -> {str(serialized_file)}")
        num_source += 1

    print(f"{num_source} files compiled and serialized")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="prepare_templates")
    parser.add_argument("-V", "--verbose", action="store_true", help="Use verbose output")
    args = parser.parse_args()

    # setup logger
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG if args.verbose else None)

    # compile and serialize templates
    prepare_templates()
