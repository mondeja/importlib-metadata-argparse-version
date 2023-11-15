import argparse
import contextlib
import io
import re

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_missing_importlib_metadata_version_from():
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
    #   missing `version` and `importlib_metadata_version_from`:
    #   safer as it happens at initialization time
    with pytest.raises(
        ValueError,
        match=(
            "Missing argument 'importlib_metadata_version_from'"
            " for ImportlibMetadataVersionAction"
        ),
    ):
        parser.add_argument('-v', action=ImportlibMetadataVersionAction)

    #   missing `version`
    parser = argparse.ArgumentParser()
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


def test_invalid_version_placeholder():
    """Not passing '%(version)s' placeholder for ``version`` at
    ``ArgumentParser`` initialization.
    """
    parser = argparse.ArgumentParser()
    parser.version = 'foo'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
        importlib_metadata_version_from='importlib_metadata_argparse_version',
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Missing '%(version)s' placeholder in"
            " ImportlibMetadataVersionAction's 'version' argument",
        ),
    ):
        parser.parse_args(['-v'])