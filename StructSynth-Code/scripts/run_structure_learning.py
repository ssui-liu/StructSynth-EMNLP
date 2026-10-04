"""Run graph induction through the installed StructSynth CLI."""
import sys

from structsynth.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["discover", *sys.argv[1:]]))
