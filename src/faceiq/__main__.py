"""Allow ``python -m faceiq`` to start the command-line application."""

from .app import main


if __name__ == "__main__":
    raise SystemExit(main())
