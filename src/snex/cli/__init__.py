from jinja2 import Environment, PackageLoader
import re
import click
import logging
from pathlib import Path

import snex

log_dfmt = "%Y-%m-%d %H:%M:%S"
log_fmt = "%(asctime)s - %(levelname)-8s - %(name)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_fmt, datefmt=log_dfmt)

logger = logging.getLogger(__name__)

env = Environment(loader=PackageLoader("snex"), autoescape=True)


@click.group()
def main():
    pass


@click.group("config")
def config_grp():
    pass


@click.command("run")
@click.argument("base_path", default=".", type=click.Path(exists=True))
@click.argument("out_path", type=click.Path(), required=False)
@click.option("--config_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-e", "--echo", count=True)
def run_cmd(base_path, out_path, config_file, echo):
    base_path = Path(base_path)
    if out_path is not None:
        out_path = Path(out_path)

    snippets = snex.extract(base_path, out_path, config_file)

    if echo > 0:
        for s in snippets:
            print("\t".join([str(entry) for entry in s[:echo]]))


@click.command("ls-templates")
def config_ls_templates_cmd():
    for t in env.list_templates():
        print(re.sub(r"\.snex\.conf", "", t))


@click.command("generate")
@click.argument("lang", required=False)
def config_generate_cmd(lang):
    tmpl = env.get_template(f"{lang}.snex.conf")
    print(tmpl.render())


main.add_command(run_cmd)
main.add_command(config_grp)
config_grp.add_command(config_generate_cmd)
config_grp.add_command(config_ls_templates_cmd)
