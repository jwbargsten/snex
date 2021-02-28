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


class Snippet:
    def __init__(self, params=None, head=None, tail=None, body=None):
        self.params = params
        self.head = head
        self.tail = tail
        self.body = body


def extract():
    conf = ConfigFactory.parse_file("snippet.conf")
    for c in _get_configs(conf):
        c.pop("name", None)
        snippets = (
            create_snippet(params, snippet_data)
            for f in _find_files(c["root"], c["glob"])
            for params, snippet_data in _extract_from_file(f, c)
        )
        out = Path(c["output_dir"])
        out.mkdir(exist_ok=True)
        for s in snippets:
            dest = out / (s.params["name"] + ".md")
            logger.info(dest)
            res = render_snippet(c["output_template"], {**c, **s.params}, s.body)
            dest.write_text(res)


def render_snippet(template, params, body):
    return pystache.render(template, {**params, **{"snippet": "\n".join(body)}})


def _get_configs(conf):
    configs = conf["config"]
    default = configs["default"] if "default" in configs else None
    for name in [n for n in configs if not n == "default"]:
        c = _merge_default(configs[name], default)
        yield c

    # EXTRACT name=hans >>>


def create_snippet(params, data):
    def is_empty(x):
        not bool(x)

    (head,) = data[:1]
    (tail,) = data[-1:]
    body = data[1:-1]

    idlvl = indent_lvl(body)

    body = (line[idlvl:] for line in body)
    body = dropwhile(is_empty, body)
    body = dropwhile_right(is_empty, list(body))

    return Snippet(
        params=params, head=head.lstrip(), body=list(body), tail=tail.lstrip()
    )


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
