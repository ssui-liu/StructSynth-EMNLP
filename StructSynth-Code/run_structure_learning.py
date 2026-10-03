"""Compatibility filename for the installed version-1 CLI."""
import sys

from structsynth.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["discover", *sys.argv[1:]]))
