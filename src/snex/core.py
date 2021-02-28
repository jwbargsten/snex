import logging
import pystache
import re
from itertools import dropwhile
import snex.util as util

logger = logging.getLogger(__name__)

DEFAULT = {
    # :snippet name=global-default-config
    "output_template": "```{{lang}}\n{{{snippet}}}\n```\n",
    "output_path": "extracted",
    "line_prefix": "",
    "comment_prefix": "# ",
    "comment_suffix": "",
    "snippet_start": ":snippet",
    "snippet_end": ":endsnippet",
    "cloak_start": ":cloak",
    "cloak_end": ":endcloak",
    "output_ext": ".md",
    # :endsnippet
}


class Snippet:
    @classmethod
    def from_raw_data(cls, params, data, origin=None, prefix=""):
        (head,) = data[:1]
        (tail,) = data[-1:]
        body = data[1:-1]

        idlvl = util.det_indent_lvl(body)

        body = (line[idlvl:] for line in body)
        body = dropwhile(util.is_empty, body)
        body = util.dropwhile_right(util.is_empty, list(body))
        body = (prefix + line for line in body)

        return cls(params=params, head=head.lstrip(), body=list(body), tail=tail.lstrip(), origin=origin)

    @property
    def name(self):
        return self.params["name"]

    def __init__(self, params=None, head=None, body=None, tail=None, origin=None):
        self.params = params
        self.head = head
        self.body = body
        self.tail = tail
        self.origin = origin

    def __repr__(self):
        return f"Snippet({self.params!r}, {self.head!r}, {self.body!r}, {self.tail!r}, {self.origin!r})"


def render_snippet(template, params, body):
    return pystache.render(template, {**params, **{"snippet": "\n".join(body)}})


def get_configs(conf):
    configs = conf["config"]
    default = configs["default"] if "default" in configs else None
    for name in [n for n in configs if not n == "default"]:
        c = util.merge_with_default_conf(configs[name], default, global_default=DEFAULT)
        # prevent defining a global name for all snippets in the config
        c.pop("name", None)
        yield (name, c)


def extract_from_file(f, conf):
    comment_prefix = re.escape(conf["comment_prefix"])
    comment_suffix = re.escape(conf["comment_suffix"])

    line_prefix = conf["line_prefix"]

    cloak_start = re.escape(conf["cloak_start"])
    cloak_end = re.escape(conf["cloak_end"])
    cloak_start_re = f"^\\s*{comment_prefix}{cloak_start}{comment_suffix}$"
    cloak_end_re = f"^\\s*{comment_prefix}{cloak_end}{comment_suffix}$"

    snippet_start = re.escape(conf["snippet_start"])
    snippet_end = re.escape(conf["snippet_end"])
    snippet_start_re = f"^\\s*{comment_prefix}{snippet_start} (.*){comment_suffix}$"
    snippet_end_re = f"^\\s*{comment_prefix}{snippet_end}{comment_suffix}$"

    snippets = []

    in_snippet = False
    cloaked = False
    data = []
    params = {}

    with open(f, "r") as fd:
        for line in fd:
            if re.search(cloak_end_re, line):
                cloaked = False
                continue
            if re.search(cloak_start_re, line):
                cloaked = True
            if cloaked:
                continue

            if match := re.search(snippet_start_re, line):
                try:
                    params = util.parse_params(match.group(1))
                except Exception as ex:
                    logger.error(f"could not parse snippet params: {line} in file {f}")
                    raise ex
                in_snippet = True
            if not in_snippet:
                continue

            data.append(line.rstrip("\n"))
            if re.search(snippet_end_re, line):
                in_snippet = False
                snippets.append(Snippet.from_raw_data(params, data, origin=f, prefix=line_prefix))
                data = []
                params = {}
    return snippets
