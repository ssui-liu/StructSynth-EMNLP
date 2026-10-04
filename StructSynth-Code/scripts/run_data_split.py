"""Run dataset splitting through the installed StructSynth CLI."""
import sys

from structsynth.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["split", *sys.argv[1:]]))
