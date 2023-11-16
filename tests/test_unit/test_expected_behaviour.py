import argparse
import contextlib
import importlib.metadata
import io

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_custom_version_scheme_from_parser():
    """Passing ``version`` at ``ArgumentParser`` initialization."""
    parser = argparse.ArgumentParser(prog='foo')
    parser.version = '%(prog)s %(version)s'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from='importlib_metadata_argparse_version',
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'foo {expected_version}\n'


def test_explicit_version_scheme_from_parser():
    """Passing '%(version)s' placeholder in ``version``
    at ``ArgumentParser`` initialization.
    """
    parser = argparse.ArgumentParser(prog='foo')
    parser.version = '%(version)s'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from='importlib_metadata_argparse_version',
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'


def test_explicit_version_scheme_from_action():
    """Passing '%(version)s' placeholder in ``version`` argument of action."""
    parser = argparse.ArgumentParser(prog='foo')
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from='importlib_metadata_argparse_version',
        version='%(version)s',
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'
