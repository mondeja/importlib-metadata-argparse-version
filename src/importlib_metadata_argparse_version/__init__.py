"""Delayed version action for argparse with importlib.metadata support."""

from __future__ import annotations

from argparse import ArgumentParser, _VersionAction


class ImportlibMetadataVersionAction(_VersionAction):
    """Delayed version action for argparse.

    An action kwarg for ``argparse.add_argument()`` which evaluates
    the version number only when the version option is passed.

    Allows to import ``importlib.metadata`` only when the
    ``--version`` option is passed to the CLI.
    """

    def __init__(  # type: ignore[no-untyped-def]
            self,
            *args,
            version_from: str = '',
            **kwargs,
    ) -> None:
        if not version_from:
            raise ValueError(
                "Missing argument 'version_from'"
                " for ImportlibMetadataVersionAction",
            )
        self.version_from = version_from
        super().__init__(*args, **kwargs)

    def __call__(  # type: ignore[no-untyped-def]
        self,
        parser: ArgumentParser,
        *args,
        **kwargs,
    ) -> None:
        """Executed when the version option is passed to the CLI."""
        # prevent default argparse behaviour because version is optional.
        #
        # if version not passed it would raises here:
        # AttributeError: 'ArgumentParser' object has no attribute 'version'
        if hasattr(parser, 'version'):
            version = parser.version
        else:
            # use '%(version)s' as default placeholder
            version = '%(version)s' if self.version is None else self.version

        if '%(version)s' not in version:
            raise ValueError(
                "Missing '%(version)s' placeholder in"
                " ImportlibMetadataVersionAction's 'version' argument",
            )

        import importlib.metadata

        # replacing here avoids `KeyError: 'prog'` when using printf
        # placeholders
        #
        # is safe because argparse uses printf placeholders
        self.version = version.replace('%(version)s', '{version}').format(
            version=importlib.metadata.version(
                self.version_from,
            ),
        )
        super().__call__(parser, *args, **kwargs)
