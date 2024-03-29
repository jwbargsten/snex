__version__ = "3000.1.1"

import logging
import snex.core as core
import snex.util as util
from pathlib import Path

logger = logging.getLogger(__name__)


def extract(base_path=None, out_path=None, config_file=None):
    if base_path is None:
        base_path = Path()

    if config_file is None:
        config_file = base_path / "snex.conf.yaml"

    processed_snippets = []
    logger.info(f"using config file {str(config_file)}")
    conf_root = util.read_yaml(config_file)
    no_snippets = True
    for conf_name, conf in core.construct_config(conf_root):
        logger.info(f"processing config {conf_name}")

        if out_path is None:
            out_path = base_path / Path(conf["output_path"])
        logger.info(f"working dir: {str(base_path)}")
        logger.info(f"output dir: {str(out_path)}")
        out_path.mkdir(exist_ok=True, parents=True)

        out_suffix = conf["output_suffix"]

        out_prefix = conf.get("output_prefix", f"{conf_name}-")

        snippets = (
            snippet
            for f in util.list_paths(conf, base_path)
            for snippet in core.extract_from_path(f, conf, base_path)
        )
        for snippet in snippets:
            no_snippets = False
            dst = out_path / f"{out_prefix}{snippet.name}{out_suffix}"
            origin = str(Path(snippet.origin).relative_to(base_path))
            logger.info(f"{origin}:{snippet.name} -> {dst}")
            processed_snippets.append((dst, snippet.name, origin, snippet.line_number))
            res = core.render_snippet(conf["output_template"], {**conf, **snippet.params}, snippet.body)
            dst.write_text(res)
    if no_snippets:
        logger.info("no snippets found")
    return processed_snippets


def load_config(f, base):
    if f is None:
        f = base / "snex.conf.yaml"

    logger.info(f"using config file {str(f)}")
    return util.read_yaml(f)


def visit(base_path=None, config_file=None):
    if base_path is None:
        base_path = Path()
    logger.info(f"working dir: {str(base_path)}")

    conf_root = load_config(config_file, base_path)

    for conf_name, conf in core.construct_config(conf_root):
        logger.info(f"processing config {conf_name}")

        out_suffix = conf["output_suffix"]

        out_prefix = conf.get("output_prefix", f"{conf_name}-")

        snippets = (
            snippet
            for f in util.list_paths(conf, base_path)
            for snippet in core.extract_from_path(f, conf, base_path)
        )
        for snippet in snippets:
            dst = f"{out_prefix}{snippet.name}{out_suffix}"
            origin = str(Path(snippet.origin).relative_to(base_path))
            if not _is_tag_match(conf, snippet.params):
                logger.info(f"Tags don't match, skipping {dst}")
                continue
            rendered = core.render_snippet(conf["output_template"], {**conf, **snippet.params}, snippet.body)
            yield {
                "snippet": snippet,
                "prefix": out_prefix,
                "suffix": out_suffix,
                "dst": dst,
                "src": origin,
                "rendered": rendered,
                "conf": conf,
            }


def _is_tag_match(conf, params):
    return not conf["tags"] or conf["tags"] & params["tags"]
