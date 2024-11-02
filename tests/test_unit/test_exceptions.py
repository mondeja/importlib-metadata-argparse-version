import argparse
import contextlib
import importlib.metadata
import io
import re

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_missing_version_argparse():
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


def test_missing_version_importlib_metadata():
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


def test_missing_version_from_importlib_metadata():
    parser = argparse.ArgumentParser()
    #   missing `version` and `version_from`
    #   version tries to be inferred from the caller module, but there is
    #   no module in this case, so it raises a ValueError
    parser.add_argument('-v', action=ImportlibMetadataVersionAction)
    with pytest.raises(
        ValueError,
        match=(
            "Argument 'version_from' for ImportlibMetadataVersionAction is"
            " missing and inferred package name from caller module"
            " 'test_exceptions' could not be found"
        ),
    ):
        parser.parse_args(['-v'])


def test_invalid_package_version_from():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        version_from='non_existent_package',
    )
    with pytest.raises(
        importlib.metadata.PackageNotFoundError,
        match='non_existent_package',
    ):
        parser.parse_args(['-v'])


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
