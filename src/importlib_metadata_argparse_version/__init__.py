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
            # try to infer package name from the caller's module
            import inspect
            import os.path

            def is_self_or_argparse_module(filename: str) -> bool:
                return filename.endswith(
                    (
                        'argparse.py',
                        os.path.join(
                            'importlib_metadata_argparse_version',
                            '__init__.py',
                        ),
                    ),
                )

            for frame_info in inspect.stack(context=2):
                if not is_self_or_argparse_module(frame_info.filename):
                    module = inspect.getmodule(frame_info.frame)
                    if module is None:
                        continue
                    # from __name__
                    version_from = getattr(module, '__name__', '__main__')
                    if version_from != '__main__':
                        setattr(self, '__version_from_inferred', True)
                        break
                    # from __package__
                    package = getattr(module, '__package__', None)
                    if package is None:
                        # from __file__
                        mfname = getattr(module, '__file__', None)
                        if mfname is None:
                            break
                        fname = os.path.basename(mfname).removesuffix('.py')
                        if fname not in ('__init__', '__main__'):
                            version_from = fname
                            setattr(self, '__version_from_inferred', True)
                    else:
                        setattr(self, '__version_from_inferred', True)
                        version_from = package
                    break

        if not version_from:
            raise ValueError(
                "Argument 'version_from' for ImportlibMetadataVersionAction is"
                " missing and package name could not be inferred from the"
                " caller module",
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

        # try to get package version from importlib.metadata
        #
        # at this point, __init__ might have inferred a bad package, so
        # we check it if here raises an import error
        try:
            package_version = importlib.metadata.version(self.version_from)
        except importlib.metadata.PackageNotFoundError as exc:
            if not hasattr(self, '__version_from_inferred'):
                raise
            raise ValueError(
                "Argument 'version_from' for ImportlibMetadataVersionAction"
                " is missing and inferred package name from caller module"
                f" '{self.version_from}' could not be found",
            ) from exc

        # replacing here avoids `KeyError: 'prog'` when using printf
        # placeholders
        #
        # is safe because argparse uses printf placeholders
        self.version = version.replace('%(version)s', '{version}').format(
            version=package_version,
        )
        super().__call__(parser, *args, **kwargs)
