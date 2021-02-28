from pyhocon import ConfigFactory, ConfigTree
from itertools import dropwhile
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


def parse_params(snippet_param_match):
    params = {}
    for kv in re.split(r"\s+", snippet_param_match.strip()):
        (k, v) = kv.split("=", 2)
        params[k.strip()] = v
    if not params["name"]:
        raise KeyError("name key not set")
    return params


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
