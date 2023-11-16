"""Delayed version action for argparse with importlib.metadata support."""

from __future__ import annotations

import argparse


class ImportlibMetadataVersionAction(argparse._VersionAction):
    """Delayed version action for argparse.

    An action kwarg for argparse.add_argument() which computes
    the version number only when the version option is passed.

    This allows to import importlib.metadata only when the
    ``--version`` option is passed to the CLI.
    """

    def __init__(  # type: ignore[no-untyped-def]
            self,
            *args,
            **kwargs,
    ) -> None:
        try:
            self.importlib_metadata_version_from = kwargs.pop(
                'importlib_metadata_version_from',
            )
        except KeyError:
            raise ValueError(
                "Missing argument 'importlib_metadata_version_from'"
                " for ImportlibMetadataVersionAction",
            ) from None
        super().__init__(*args, **kwargs)

    def __call__(  # type: ignore[no-untyped-def]
        self,
        parser: argparse.ArgumentParser,
        *args,
        **kwargs,
    ) -> None:
        """Executed when the version option is passed to the CLI."""
        # prevent default argparse behaviour because version is optional:
        # https://github.com/python/cpython/blob/86a5e22dfe77558d2e2609c70d1d9e27274a63c0/Lib/argparse.py
        #
        # if version not passed raises here:
        # AttributeError: 'ArgumentParser' object has no attribute 'version'
        try:
            version = parser.version  # type: ignore[attr-defined]
        except AttributeError:
            # use '%(version)s' as default placeholder
            version = '%(version)s' if self.version is None else self.version

        if '%(version)s' not in version:
            raise ValueError(
                "Missing '%(version)s' placeholder in"
                " ImportlibMetadataVersionAction's 'version' argument",
            )

        import importlib.metadata as importlib_metadata

        # replacing here avoids `KeyError: 'prog'` when using printf
        # placeholders
        #
        # seems safe because argparse uses printf placeholders
        self.version = version.replace('%(version)s', '{version}').format(
            version=importlib_metadata.version(
                self.importlib_metadata_version_from,
            ),
        )
        super().__call__(parser, *args, **kwargs)
