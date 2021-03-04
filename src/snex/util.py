from pyhocon import ConfigFactory, ConfigTree
from itertools import dropwhile
from pathlib import Path
import logging
import re

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

logger = logging.getLogger(__name__)


VALID_NAME_RE = r"[^-0-9A-Za-z_.%~äßöüÄ§ÖÜ€áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+"


def construct_params(snippet_param_match, path, lnum ):
    data = re.split(r"\s+", snippet_param_match.strip(), maxsplit=1)
    params = { "path": str(path), "lnum": lnum }
    if data and data[0]:
        params["name"] = data[0]
    else:
        params["name"] = f"{str(path)}-{lnum}"

    extra = load("{ " + data[1] + " }", Loader=Loader) if len(data) > 1 else { }
    x = {**extra, **params}
    return x


# :snippet def-sanitize-for-filename
def sanitize_for_file_name(v):
    return re.sub(VALID_NAME_RE, "-", v)
# :endsnippet

def sanitize_params(params, valid_keys):
    if not ("name" in params and params["name"]):
        raise KeyError("name key not set")
    params["name"] = sanitize_for_file_name(params["name"])
    return {k: v for k, v in params.items() if k in valid_keys}


def find_files(root, glob):
    logger.info(f"{root} -> {glob}")
    for p in Path(root).glob(glob):
        if p.is_file():
            yield p


def det_indent_lvl(lines):
    return min([len(x) - len(x.lstrip()) for x in lines if x])


def dropwhile_right(pred, seq):
    return reversed(list(dropwhile(pred, reversed(seq))))


def merge_with_default_conf(conf, default_conf=None, global_default=None):
    if global_default is None:
        global_default = {}
    if default_conf is None:
        default_conf = ConfigTree()

    tmp = ConfigTree.merge_configs(ConfigFactory.from_dict(global_default), default_conf, copy_trees=True)
    return ConfigTree.merge_configs(tmp, conf)


def is_empty(x):
    return not bool(x)
