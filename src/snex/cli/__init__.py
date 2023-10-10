from jinja2 import Environment, PackageLoader
import re
import json
from snex.util import run_cmd as run_shell_cmd
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
        print(re.sub(r"\.snex\.conf.yaml", "", t))


@click.command("generate")
@click.argument("lang", required=True)
def config_generate_cmd(lang):
    tmpl = env.get_template(f"{lang}.snex.conf.yaml")
    print(tmpl.render())


@click.command("gist")
@click.argument("base_path", default=".", type=click.Path(exists=True))
@click.option("--config_file", type=click.Path(exists=True, dir_okay=False))
def gist_cmd(base_path, config_file):
    base_path = Path(base_path)
    gists_path = base_path / ".github" / "snex-gists.json"

    gists = {}
    if gists_path.exists():
        gists = json.loads(gists_path.read_text())

    for snippet in snex.visit(base_path, config_file):
        if "gist" not in snippet["snippet"].params["tags"] or "gist" not in snippet["conf"]["tags"]:
            logger.info(f"skipping {snippet['dst']}")
            continue

        dst = f"{snippet['dst']}"
        if dst in gists:
            logger.info(f"publishing gist (u) {dst}")
            out, err = run_shell_cmd(
                ["gh", "gist", "edit", gists[dst], "-", "-a", dst],
                capture=True,
                in_=snippet["rendered"],
                verbose=True,
            )
        else:
            logger.info(f"publishing gist (c) {dst}")
            out, err = run_shell_cmd(
                ["gh", "gist", "create", "-f", dst], capture=True, in_=snippet["rendered"], verbose=True
            )
            gists[dst] = out.strip()
        if err.strip():
            logger.info("\n" + err)
        if out.strip():
            logger.info(out)

    if gists:
        gists_path.parent.mkdir(exist_ok=True)
        gists_path.write_text(json.dumps(gists, indent=2))


main.add_command(gist_cmd)
main.add_command(run_cmd)
main.add_command(config_grp)
config_grp.add_command(config_generate_cmd)
config_grp.add_command(config_ls_templates_cmd)
