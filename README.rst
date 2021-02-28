snex - snippet extractor
========================

Extract snippets for blog posts or examples.

How to use

Installation
------------

::

   pip install snex

Setup
-----

create a snex.conf in the root directory of a project you want to create
snippets from:

::

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
`HOCON <https://github.com/typesafehub/config/blob/master/HOCON.md>`__,
under the hood `pyhocon <https://github.com/chimpler/pyhocon>`__.

You have 3 layers of settings in a section:

1. the global default config
   ```docs/snippets/global-default-config.md`` <docs/snippets/global-default-config.md>`__.
2. the config section ``default`` in your ``snex.conf`` file (which
   overwrites the global default).
3. the specific config section in your ``snex.conf`` (the section name
   is only for the show, it does not have any effect. Only ``default``
   is reserved.). The configuration in a specific section overwrites the
   default section which overwrites the global default config.

Run
---

Let’s assume that you have a project in ``/path/to/your/project``. You
created a ``/path/to/your/project/snex.conf`` like described in the
previous topic.

From the project directory
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   cd /path/to/your/project
   snex

This will read ``snex.conf`` in the current directory and dump the
snippets into the configured ``output_path``.

From a different directory
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   snex /path/to/your/project

This will read ``/path/to/your/project/snex.conf`` and dump the snippets
into the configured ``output_path``.

From a different directory to a different snippet output directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   snex /path/to/your/project /path/custom/snippet/output/dir

This will read ``/path/to/your/project/snex.conf`` and dump the snippets
into ``/path/custom/snippet/output/dir``.

**TAKE CARE**

This invocation will overwrite the output dir of all defined config
sections. Which means that all snippets are dumped into the same
directory.
