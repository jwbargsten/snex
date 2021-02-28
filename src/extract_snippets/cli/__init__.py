import click
import logging

import extract_snippets
log_dfmt = "%Y-%m-%d %H:%M:%S"
log_fmt = "%(asctime)s - %(levelname)-8s - %(name)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_fmt, datefmt=log_dfmt)

logger = logging.getLogger(__name__)


@click.command()
def main():
    extract_snippets.extract()


if __name__ == "__main__":
    main()
