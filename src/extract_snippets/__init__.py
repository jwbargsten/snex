__version__ = "0.1.0"

import logging
from pyhocon import ConfigFactory
import extract_snippets.core as core
import extract_snippets.util as util
from pathlib import Path

logger = logging.getLogger(__name__)


def extract(base_path=None, out_base_path=None):
    if base_path is None:
        base_path = Path()
    if out_base_path is None:
        out_base_path = base_path

    conf_root = ConfigFactory.parse_file(base_path / "snippet.conf")
    no_snippets = True
    for conf in core.get_configs(conf_root):
        # prevent defining a global name for all snippets in the config
        conf.pop("name", None)
        snippets = (
            snippet
            for f in util.find_files(conf["root"], conf["glob"])
            for snippet in core.extract_from_file(f, conf)
        )
        out_path = Path(conf["output_path"])
        if not out_path.is_absolute():
            out_path = out_base_path / out_path
        out_path.mkdir(exist_ok=True)
        for snippet in snippets:
            no_snippets = False
            name = snippet.params["name"]
            dst = out_path / (name + ".md")
            logger.info(f"writing snippet {name} to {dst}")
            res = core.render_snippet(conf["output_template"], {**conf, **snippet.params}, snippet.body)
            dst.write_text(res)
    if no_snippets:
        logger.info("no snippets found")
