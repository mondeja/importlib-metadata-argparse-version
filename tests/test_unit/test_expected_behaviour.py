import argparse
import contextlib
import importlib.metadata
import io
import sys

import pytest

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction


def test_custom_version_scheme_from_parser():
    """Passing ``version`` at ``ArgumentParser`` initialization."""
    parser = argparse.ArgumentParser(prog='foo')
    parser.version = '%(prog)s %(version)s'
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
        version_from='importlib_metadata_argparse_version',
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
        version_from='importlib_metadata_argparse_version',
        version='%(version)s',
    )

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'


def test_infer_version_from___name__():
    """Infer package name from caller module's __name__."""
    parser = argparse.ArgumentParser(prog='foo')
    # mock module name
    prev_module_name = __name__
    module = sys.modules[prev_module_name]
    module.__name__ = 'importlib_metadata_argparse_version'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'
    module.__name__ = prev_module_name


def test_infer_version_from___package__():
    """Infer package name from caller's module __package__."""
    parser = argparse.ArgumentParser(prog='foo')
    # mock module name and package
    prev_module_name = __name__
    module = sys.modules[prev_module_name]
    module.__name__ = '__main__'
    module.__package__ = 'importlib_metadata_argparse_version'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'
    delattr(module, '__package__')
    module.__name__ = prev_module_name


def test_infer_version_from___file__():
    """Infer package name from caller's module __file__."""
    parser = argparse.ArgumentParser(prog='foo')
    # mock module name and package
    prev_module_name = __name__
    module = sys.modules[prev_module_name]
    module.__name__ = '__main__'
    module.__file__ = 'importlib_metadata_argparse_version.py'
    parser.add_argument(
        '-v',
        action=ImportlibMetadataVersionAction,
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), pytest.raises(SystemExit):
        parser.parse_args(['-v'])

    expected_version = importlib.metadata.version(
        'importlib_metadata_argparse_version',
    )
    assert stdout.getvalue() == f'{expected_version}\n'
    delattr(module, '__file__')
    module.__name__ = prev_module_name
