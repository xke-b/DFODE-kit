"""Compatibility shim for :mod:`dfode_kit.cli.main`."""

from dfode_kit.cli.main import *  # noqa: F401,F403


if __name__ == "__main__":
    raise SystemExit(main())
