"""Tests for ``importlib_metadata_argparse_version`` module.

NOTE: it is located at tests/ directory to allow setuptools install
without additional exclusion configuration.
"""

import argparse
import contextlib
import io
import os
import sys

import pytest

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


self_modname = os.path.basename(os.path.dirname(os.path.dirname(__file__))).replace(
    "-", "_"
)
self_version = importlib_metadata.version(self_modname)

importlib_metadata_modname = (
    "importlib_metadata" if sys.version_info < (3, 8) else "importlib.metadata"
)
del sys.modules[importlib_metadata_modname]


def test_rationale():
    """Assert that this module avoids to import ``importlib.metadata``
    until an ``--version`` option is passed to the CLI.
    """
    if importlib_metadata_modname in sys.modules:
        del sys.modules[importlib_metadata_modname]

    efficient_parser = argparse.ArgumentParser()
    efficient_parser.add_argument(
        "-v",
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from=self_modname,
    )
    assert importlib_metadata_modname not in sys.modules

    try:
        import importlib.metadata as importlib_metadata
    except ImportError:
        import importlib_metadata

    unefficient_parser = argparse.ArgumentParser()
    unefficient_parser.add_argument(
        "-v",
        action="version",
        version=importlib_metadata.version(self_modname),
    )
    assert importlib_metadata_modname in sys.modules
    del sys.modules[importlib_metadata_modname]

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        with pytest.raises(SystemExit):
            efficient_parser.parse_args(["-v"])
        assert importlib_metadata_modname in sys.modules
        del sys.modules[importlib_metadata_modname]

        with pytest.raises(SystemExit):
            unefficient_parser.parse_args(["-v"])
        # when called, is not readded
        assert importlib_metadata_modname not in sys.modules

    efficient_version, unefficient_version = [
        v for v in stdout.getvalue().split("\n") if v
    ]
    assert efficient_version == unefficient_version


def test_missing_kwargs():
    """This module makes the ``version`` kwarg optional, while argparse
    makes it mandatory, raising an ``AttributeError`` if is not defined.
    """
    # argparse behaviour
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", action="version")
    with pytest.raises(
        AttributeError, match="'ArgumentParser' object has no attribute 'version'"
    ):
        parser.parse_args(["-v"])

    # module behaviour
    parser = argparse.ArgumentParser()
    #   missing `version` and `importlib_metadata_version_from`:
    #   safer as it happens at initialization time
    with pytest.raises(
        ValueError,
        match="Missing kwarg 'importlib_metadata_version_from' for ImportlibMetadataVersionAction",
    ):
        parser.add_argument("-v", action=ImportlibMetadataVersionAction)

    #   missing `version`
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from=self_modname,
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        with pytest.raises(SystemExit):
            parser.parse_args(["-v"])
    assert stdout.getvalue() == f"{self_version}\n"


def test_version_from_parser():
    """Passing ``version`` at ``ArgumentParser`` initialization."""
    parser = argparse.ArgumentParser(prog="foo")
    parser.version = "%(prog)s %(version)s"
    parser.add_argument(
        "-v",
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from=self_modname,
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        with pytest.raises(SystemExit):
            parser.parse_args(["-v"])
    assert stdout.getvalue() == f"foo {self_version}\n"
