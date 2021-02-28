__version__ = "0.1.0"

import logging
from pyhocon import ConfigFactory
import extract_snippets.core as core
import extract_snippets.util as util
from pathlib import Path

logger = logging.getLogger(__name__)


def extract(base_path=None, out_path=None):
    if base_path is None:
        base_path = Path()

    conf_root = ConfigFactory.parse_file(base_path / "snippet.conf")
    no_snippets = True
    for conf_name, conf in core.get_configs(conf_root):
        logger.info(f"processing config {conf_name}")

        if out_path is None:
            out_path = Path(conf["output_path"])
        if not out_path.is_absolute():
            out_path = base_path / out_path
        logger.info(f"working dir: {str(base_path)}")
        logger.info(f"output dir: {str(out_path)}")
        out_path.mkdir(exist_ok=True, parents=True)

        out_ext = conf["output_ext"]

        snippets = (
            snippet
            for f in util.find_files(base_path / conf["root"], conf["glob"])
            for snippet in core.extract_from_file(f, conf)
        )
        for snippet in snippets:
            no_snippets = False
            dst = out_path / (snippet.name + out_ext)
            origin = str(Path(snippet.origin).relative_to(base_path))
            logger.info(f"{origin}:{snippet.name} -> {dst}")
            res = core.render_snippet(conf["output_template"], {**conf, **snippet.params}, snippet.body)
            dst.write_text(res)
    if no_snippets:
        logger.info("no snippets found")
