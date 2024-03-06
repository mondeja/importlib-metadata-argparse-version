import argparse
import contextlib
import importlib.metadata
import io
import re

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_missing_version_from():
    """This module makes the ``version`` kwarg optional, while argparse
    makes it mandatory, raising an ``AttributeError`` if is not defined.
    """
    # argparse behaviour
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='version')
    with pytest.raises(
        AttributeError,
        match="'ArgumentParser' object has no attribute 'version'",
    ):
        parser.parse_args(['-v'])

    # module behaviour
    parser = argparse.ArgumentParser()
    #   missing `version` and `version_from`:
    #   safer as it happens at initialization time
    with pytest.raises(
        ValueError,
        match=(
            "Missing argument 'version_from'"
            " for ImportlibMetadataVersionAction"
        ),
    ):
        parser.add_argument('-v', action=ImportlibMetadataVersionAction)

    #   missing `version`
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        version_from='importlib_metadata_argparse_version',
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'


def test_invalid_version_placeholder_from_parser():
    """Not passing '%(version)s' placeholder for ``version`` at
    ``ArgumentParser`` initialization.
    """
    parser = argparse.ArgumentParser()
    parser.version = 'foo'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        version_from='importlib_metadata_argparse_version',
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Missing '%(version)s' placeholder in"
            " ImportlibMetadataVersionAction's 'version' argument",
        ),
    ):
        parser.parse_args(['-v'])


def test_invalid_version_placeholder_from_action():
    """Not passing '%(version)s' placeholder for ``version``
    at action initialization.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        version_from='importlib_metadata_argparse_version',
        version='foo',
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Missing '%(version)s' placeholder in"
            " ImportlibMetadataVersionAction's 'version' argument",
        ),
    ):
        parser.parse_args(['-v'])
