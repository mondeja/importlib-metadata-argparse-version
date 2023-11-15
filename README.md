# `importlib-metadata-argparse-version`

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Python versions][pypi-pyversions-badge-link]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]

Python's [`argparse`] module action to define CLI version with a delayed
call to [`importlib.metadata.version`] only when `--version` argument
is passed.

## Rationale

When you use `importlib.metadata` for adding the version to a CLI utility,
you need to import `importlib.metadata` and call
`importlib.metadata.version("<your-package>")` at initialization time.
If you only want to execute other part of the CLI
(eg. like with the argument `--help`), `importlib.metadata` will be imported
too even when is not needed at all.

The problem is easily fixed by this module.

## Usage

```python
import argparse

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction

parser = argparse.ArgumentParser()
parser.add_argument(
    "-v", "--version",
    action=ImportlibMetadataVersionAction,
    importlib_metadata_version_from="your-module-name",
)
```

This is a rough equivalent to something like:

```python
import argparse
import importlib.metadata

parser = argparse.ArgumentParser()
parser.add_argument(
    "-v", "--version",
    action="version",
    version=importlib_metadata.version("your-module-name"),
)
```

...but with the difference that `importlib.metadata` will only be
imported when you call `--version`, so it is more efficient.

When using `ImportlibMetadataVersionAction` the `version` kwarg
accepts `%(version)s` as a placeholder like `%(prog)s`. So you
can write something like this to display the program name before the
version:

```python
parser.add_argument(
    "-v", "--version",
    action=ImportlibMetadataVersionAction,
    importlib_metadata_version_from="your-module-name",
    version="%(prog)s %(version)s",
)

# or

parser.version = "%(prog)s %(version)s"
parser.add_argument(
    "-v", "--version",
    action=ImportlibMetadataVersionAction,
    importlib_metadata_version_from="your-module-name",
)
```

And the `version` kwarg becomes optional, being `"%(version)s"`
the default value.

## For convenience

If you forget to define the kwarg `importlib_metadata_version_from`
in the argument, a `ValueError` will be raised at initialization time.
Python's [`argparse`] built-in `"version"` action raises an
`AttributeError` only when you call your program with `--version` when
you forget to define the `version` kwarg, which is less safer because
could lead you to pass the error unexpected until you test it.
And `--version` checking is a really dumb test.

[`argparse`]: https://docs.python.org/3/library/argparse.html
[`importlib.metadata.version`]: https://docs.python.org/3/library/importlib.metadata.html?highlight=importlib%20metadata#distribution-versions
[pypi-link]: https://pypi.org/project/importlib-metadata-argparse-version
[pypi-version-badge-link]: https://img.shields.io/pypi/v/importlib-metadata-argparse-version?logo=pypi&logoColor=white
[pypi-pyversions-badge-link]: https://img.shields.io/pypi/pyversions/importlib-metadata-argparse-version?logo=python&logoColor=white
[license-image]: https://img.shields.io/pypi/l/importlib-metadata-argparse-version?color=light-green&logo=freebsd&logoColor=white
[license-link]: https://github.com/mondeja/importlib-metadata-argparse-version/blob/master/LICENSE
[tests-image]: https://img.shields.io/github/actions/workflow/status/mondeja/importlib-metadata-argparse-version/ci.yml?logo=github&label=tests&branch=master
[tests-link]: https://github.com/mondeja/importlib-metadata-argparse-version/actions?query=workflow%3ACI
[coverage-image]: https://img.shields.io/codecov/c/github/mondeja/importlib-metadata-argparse-version?logo=codecov&logoColor=white
[coverage-link]: https://app.codecov.io/gh/mondeja/importlib-metadata-argparse-version
