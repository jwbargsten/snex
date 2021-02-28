__version__ = "0.1.0"

import logging
import pystache
import re
from pathlib import Path
from itertools import dropwhile
from pyhocon import ConfigFactory, ConfigTree

logger = logging.getLogger(__name__)

DEFAULT = {
    "output_template": "```{{lang}}\n{{snippet}}\n```\n",
    "output_dir": "extracted",
    "comment_prefix": "# ",
    "comment_suffix": "",
}


def extract():
    conf = ConfigFactory.parse_file("snippet.conf")
    for c in _get_configs(conf):
        c.pop("name", None)
        snippets = (
            (s[0], sanitize_snippet(s[1]))
            for f in _find_files(c["root"], c["glob"])
            for s in _extract_from_file(f, c)
        )
        out = Path(c["output_dir"])
        out.mkdir(exist_ok=True)
        for (params, snippet) in snippets:
            dest = out / (params["name"] + ".md")
            logger.info(dest)
            logger.info(params)
            res = render_snippet(c["output_template"], {**c, **params}, snippet)
            dest.write_text(res)


def render_snippet(template, params, snippet):
    p = {**params, **{"snippet": "\n".join(snippet[1])}}
    return pystache.render(template, p)


def _get_configs(conf):
    configs = conf["config"]
    default = configs["default"] if "default" in configs else None
    for name in [n for n in configs if not n == "default"]:
        c = _merge_default(configs[name], default)
        # logger.info(f"config: {c}")
        yield c

    # EXTRACT name=hans >>>


def sanitize_snippet(s):
    def is_empty(x):
        not bool(x)

    (head,) = s[:1]
    (tail,) = s[-1:]
    body = s[1:-1]
    idlvl = indent_lvl(body)
    logger.info(f"sanitize {idlvl=}")
    body = (line[idlvl:] for line in body)
    body = dropwhile(is_empty, body)
    body = dropwhile_right(is_empty, list(body))
    return (head.lstrip(), list(body), tail.lstrip())


def indent_lvl(lines):
    return min([len(x) - len(x.lstrip()) for x in lines if x])


def dropwhile_right(pred, seq):
    return reversed(list(dropwhile(pred, reversed(seq))))


def _extract_from_file(f, conf):
    comment_prefix = re.escape(conf["comment_prefix"])
    comment_suffix = re.escape(conf["comment_suffix"])
    # EXTRACT <<<

    cloak_end_re = f"^\\s*{comment_prefix}CLOAK <<<{comment_suffix}$"
    cloak_start_re = f"^\\s*{comment_prefix}CLOAK >>>{comment_suffix}$"
    snippet_start_re = f"^\\s*{comment_prefix}EXTRACT (.*)\\s*>>>{comment_suffix}$"
    snippet_end_re = f"^\\s*{comment_prefix}EXTRACT <<<{comment_suffix}$"

    snippets = []

    in_snippet = False
    cloaked = False
    snippet = []
    params = {}

    with open(f, "r") as fd:
        # EXTRACT name=julia lang=x>>>
        for line in fd:
            if re.search(cloak_end_re, line):
                cloaked = False
            if re.search(cloak_start_re, line):
                cloaked = True
            if cloaked:
                continue

            if match := re.search(snippet_start_re, line):
                params = to_dict(match.group(1).strip())
                if not params["name"]:
                    raise KeyError("name key not set")
                in_snippet = True
            if not in_snippet:
                continue

            snippet.append(line.rstrip("\n"))
            if re.search(snippet_end_re, line):
                in_snippet = False
                snippets.append((params, snippet))
                snippet = []
                params = {}
    return snippets

    # EXTRACT <<<


def to_dict(s):
    d = {}
    for kv in re.split(r"\s+", s):
        (k, v) = kv.split("=", 2)
        d[k.strip()] = v.strip()
    return d


def _find_files(root, glob):
    logger.info(f"{root} -> {glob}")
    for p in Path(root).glob(glob):
        yield p


def _merge_default(config, default=None):
    if default is None:
        default = ConfigTree()

    tmp = ConfigTree.merge_configs(
        ConfigFactory.from_dict(DEFAULT), default, copy_trees=True
    )
    return ConfigTree.merge_configs(tmp, config)
