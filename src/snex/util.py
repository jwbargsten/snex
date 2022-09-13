from itertools import dropwhile
from pathlib import Path
import os
import logging
import re
import requests as rq

from yaml import safe_load

logger = logging.getLogger(__name__)


VALID_NAME_RE = r"[^-0-9A-Za-z_.%~äßöüÄ§ÖÜ€áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+"

# https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45

url_regex = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def is_url(value):
    return bool(url_regex.search(str(value)))


def read_yaml(f):
    with open(f, "r") as fd:
        return safe_load(fd)


def construct_params(snippet_param_match, path, base_path, lnum):
    data = re.split(r"\s+", snippet_param_match.strip(), maxsplit=1)
    params = {"lnum": lnum}
    if is_url(path):
        params["fname"] = re.sub(r"^.*/", "", str(path).rstrip("/"))
        params["path"] = path
    else:
        params["fname"] = Path(path).name
        params["path"] = os.path.relpath(str(Path(path).absolute()), start=str(base_path))
    if data and data[0]:
        params["name"] = data[0]
    else:
        params["name"] = f"{str(path)}-{lnum}"

    extra = safe_load("{ " + data[1] + " }") if len(data) > 1 else {}

    return {**extra, **params}


def read_path(path):
    if is_url(path):
        res = rq.get(path)
        for idx, line in enumerate(res.text.splitlines()):
            yield (idx, line)
    else:
        with open(path, "r") as fd:
            for idx, line in enumerate(fd):
                yield (idx, line)


def list_paths(conf, base_path):
    if "path" in conf:
        if is_url(conf["path"]):
            yield conf["path"]
        else:
            p = Path(conf["path"])
            if not p.is_absolute:
                p = base_path / p
            if p.is_file:
                yield p
    else:
        for f in find_files(base_path / conf["root"], conf["glob"]):
            yield f


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
    if not lines:
        return 0
    return min([len(x) - len(x.lstrip()) for x in lines if x])


def dropwhile_right(pred, seq):
    return reversed(list(dropwhile(pred, reversed(seq))))


def merge_with_default_conf(conf, default_conf=None, global_default=None):
    if global_default is None:
        global_default = {}
    if default_conf is None:
        default_conf = {}
    return {**global_default, **default_conf, **conf}


def is_empty(x):
    return not bool(x)
