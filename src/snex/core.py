import logging
import chevron
import re
from itertools import dropwhile
import snex.util as util

logger = logging.getLogger(__name__)

DEFAULT = {
    # :snippet global-default-config lang: python
    "output_template": "```{{lang}}\n{{{snippet}}}\n```\n",
    "valid_param_keys": ["name", "lang", "lnum", "fname", "path", "tags"],
    "output_path": "snippets",
    "line_prefix": "",
    "comment_prefix": "# ",
    "comment_suffix": "",
    "snippet_start": ":snippet",
    "snippet_end": ":endsnippet",
    "cloak_start": ":cloak",
    "cloak_end": ":endcloak",
    "output_suffix": ".md",
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

    @property
    def line_number(self):
        return self.params.get("lnum", -1)

    def __init__(self, params=None, head=None, body=None, tail=None, origin=None):
        self.params = params
        self.head = head
        self.body = body
        self.tail = tail
        self.origin = origin

    def __repr__(self):
        return f"Snippet({self.params!r}, {self.head!r}, {self.body!r}, {self.tail!r}, {self.origin!r})"

    def as_dict(self):
        return {
            "params": self.params,
            "head": self.head,
            "body": self.body,
            "tail": self.tail,
            "origin": self.origin,
        }


def render_snippet(template, params, body):
    return chevron.render(template, {**params, **{"snippet": "\n".join(body)}})


def construct_config(conf):
    default = conf["default"] if "default" in conf else None
    for name in [n for n in conf if not n == "default"]:
        c = util.merge_with_default_conf(conf[name], default, global_default=DEFAULT)
        # prevent defining a global name for all snippets in the config
        c.pop("name", None)

        c["tags"] = util.parse_tags(c.get("tags"))
        yield (name, c)


def extract_from_path(f, conf, base_path):
    comment_prefix = re.escape(conf["comment_prefix"])
    comment_suffix = re.escape(conf["comment_suffix"])

    line_prefix = conf["line_prefix"]

    cloak_start = re.escape(conf["cloak_start"])
    cloak_end = re.escape(conf["cloak_end"])
    cloak_start_re = f"^\\s*{comment_prefix}{cloak_start}{comment_suffix}$"
    cloak_end_re = f"^\\s*{comment_prefix}{cloak_end}{comment_suffix}$"

    snippet_start = re.escape(conf["snippet_start"])
    snippet_end = re.escape(conf["snippet_end"])
    snippet_start_re = f"^\\s*{comment_prefix}{snippet_start}(.*){comment_suffix}$"
    snippet_end_re = f"^\\s*{comment_prefix}{snippet_end}{comment_suffix}$"

    result_snippets = []

    cloaked = False

    tmp_snippets = []

    for idx, line in util.read_path(f):
        lnum = idx + 1
        if re.search(cloak_end_re, line):
            cloaked = False
            continue
        if re.search(cloak_start_re, line):
            cloaked = True
        if cloaked:
            continue

        if re.search(snippet_end_re, line):
            snippet = tmp_snippets.pop()
            snippet["data"].append(line.rstrip("\n"))
            s = Snippet.from_raw_data(snippet["params"], snippet["data"], origin=f, prefix=line_prefix)
            result_snippets.append(s)
            continue

        if match := re.search(snippet_start_re, line):
            try:
                params = util.construct_params(match.group(1), f, base_path, lnum)
                tmp_snippets.append(
                    {"params": util.sanitize_params(params, conf["valid_param_keys"]), "data": [line]}
                )
            except Exception as ex:
                logger.error(f"could not parse snippet params: {line} in file {f}:{lnum}")
                raise ex
            continue

        for snippet in tmp_snippets:
            snippet["data"].append(line.rstrip("\n"))

    return result_snippets
