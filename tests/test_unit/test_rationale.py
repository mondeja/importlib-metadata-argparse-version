import argparse
import contextlib
import io
import sys

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_rationale_efficient_parser():
    """Assert that this module avoids to import ``importlib.metadata``
    until a ``--version`` option is passed to the CLI.
    """
    if 'importlib.metadata' in sys.modules:
        del sys.modules['importlib.metadata']
    assert 'importlib.metadata' not in sys.modules

    # create a parser with the efficient version action
    efficient_parser = argparse.ArgumentParser()
    efficient_parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from='importlib_metadata_argparse_version',
    )
    assert 'importlib.metadata' not in sys.modules
    # call the parser with the version option
    with pytest.raises(SystemExit):
        efficient_parser.parse_args(['-v'])
    assert 'importlib.metadata' in sys.modules


def test_rationale_unefficient_parser():
    if 'importlib.metadata' in sys.modules:
        del sys.modules['importlib.metadata']
    assert 'importlib.metadata' not in sys.modules

    # create a parser with the unefficient version action
    import importlib.metadata
    unefficient_parser = argparse.ArgumentParser()
    unefficient_parser.add_argument(
        '-v',
        action='version',
        version=importlib.metadata.version(
            'importlib_metadata_argparse_version'),
    )
    assert 'importlib.metadata' in sys.modules


def test_parsers_version_consistency():
    import importlib.metadata

    unefficient_parser = argparse.ArgumentParser()
    unefficient_parser.add_argument(
        '-v',
        action='version',
        version=importlib.metadata.version(
            'importlib_metadata_argparse_version'),
    )

    efficient_parser = argparse.ArgumentParser()
    efficient_parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from='importlib_metadata_argparse_version',
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        with pytest.raises(SystemExit):
            efficient_parser.parse_args(['-v'])

        with pytest.raises(SystemExit):
            unefficient_parser.parse_args(['-v'])

    efficient_version, unefficient_version = (
        vers for vers in stdout.getvalue().split('\n') if vers
    )
    assert efficient_version == unefficient_version
