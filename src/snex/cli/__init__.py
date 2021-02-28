import click
import logging
from pathlib import Path

import snex
log_dfmt = "%Y-%m-%d %H:%M:%S"
log_fmt = "%(asctime)s - %(levelname)-8s - %(name)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_fmt, datefmt=log_dfmt)

logger = logging.getLogger(__name__)


@click.command()
@click.argument('base_path', default=".", type=click.Path(exists=True))
@click.argument('out_path', type=click.Path(), required=False)
def main(base_path, out_path):
    base_path = Path(base_path)
    if out_path is not None:
        out_path = Path(out_path)

    snex.extract(base_path, out_path)


if __name__ == "__main__":
    main()
