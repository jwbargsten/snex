# snex - snippet extractor

Extract snippets for blog posts or examples.

How to use

## Installation

    pip install snex

## Tag Snippets

Let's assume that you have a project in `/path/to/your/project`. You navigate to the
region where you want to extract a snippet and tag it as follows (`# ` is regarded as
comment prefix):

    # :snippet snippet-name-without-whitespace

    def foobar():
       doit()
    foobar()

    # :endsnippet

- Empty lines after the start and before the end are removed.
- _A snippet name is mandatory._
- The snippet `name` is sanitized to prevent malicious code to overwrite arbitrary files
  on your system.

### Advanced snippet tagging

You can also overwrite the `lang` config to use a different language for this snippet.

```
# :snippet snippet-name-without-whitespace lang: scala
```

Everything after the snippet name is parsed as YAML dict:
`{ $text_after_snippet_name }`, e.g. `lang: scala, other_param: "hello world"` is parsed as `{ lang: scala, other_param: "hello world" }` YAML.

This means that you can also customise your parameter substitutions with a config like:

```
config {
  default {
    "output_template": "```{{lang}} - {{other_param}}\n{{{snippet}}}\n```\n",
    "valid_param_keys": [ "lang", "name", "other_param" ]
    ...
  }
}
```

The output template is parsed as [mustache template](https://mustache.github.io/).

## Setup

create a snex.conf in the root directory of a project you want to create snippets from:

    config {
      default {
        output_path: "snippets"
        comment_prefix: "# "
        comment_suffix: ""
      }

      src {
        lang: "python"
        root: "src"
        glob: "**/*.py"
      }
    }

The config syntax is
[HOCON](https://github.com/typesafehub/config/blob/master/HOCON.md), under the hood
[pyhocon](https://github.com/chimpler/pyhocon).

You have 3 layers of settings in a section:

1.  [the global default config](docs/snippets/global-default-config.md) in
    `docs/snippets/global-default-config.md`
2.  the config section `default` in your `snex.conf` file (which overwrites the global
    default).
3.  the specific config section in your `snex.conf` (the section name is only for the
    show, it does not have any effect. Only `default` is reserved.). The configuration
    in a specific section overwrites the default section which overwrites the global
    default config.

## Run

You created a `/path/to/your/project/snex.conf` like described in the previous topic.

### From the project directory

    cd /path/to/your/project
    snex

This will read `snex.conf` in the current directory and dump the snippets into the
configured `output_path`.

### From a different directory

    snex /path/to/your/project

This will read `/path/to/your/project/snex.conf` and dump the snippets into the
configured `output_path`.

### From a different directory to a different snippet output directory

    snex /path/to/your/project /path/custom/snippet/output/dir

This will read `/path/to/your/project/snex.conf` and dump the snippets into
`/path/custom/snippet/output/dir`.

**TAKE CARE**

This invocation will overwrite the output dir of all defined config sections. Which
means that all snippets are dumped into the same directory.

## Caveats (or features)

- Snippets are overwritten without confirmation. This makes it easy to update
  everything, but you have to take care that you will not overwrite stuff you want to
  keep.
