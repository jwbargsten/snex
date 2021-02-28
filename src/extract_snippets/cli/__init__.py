import click
import logging
from pathlib import Path

import extract_snippets
log_dfmt = "%Y-%m-%d %H:%M:%S"
log_fmt = "%(asctime)s - %(levelname)-8s - %(name)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_fmt, datefmt=log_dfmt)

logger = logging.getLogger(__name__)


@click.command()
@click.argument('base_path', default=".", type=click.Path(exists=True))
@click.argument('out_base_path', type=click.Path(), required=False)
def main(base_path, out_base_path):
    if out_base_path is None:
        out_base_path = base_path
    logger.info(f"{base_path=}, {out_base_path=}")
    extract_snippets.extract(Path(base_path), Path(out_base_path))


if __name__ == "__main__":
    main()
