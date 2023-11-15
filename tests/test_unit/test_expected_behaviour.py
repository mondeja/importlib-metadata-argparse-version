import argparse
import contextlib
import io

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_custom_version_scheme():
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

    import importlib.metadata
    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'foo {expected_version}\n'


def test_version_scheme_explicit_default_placeholder():
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

    import importlib.metadata
    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'
