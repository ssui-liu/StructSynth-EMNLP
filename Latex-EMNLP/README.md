# StructSynth EMNLP LaTeX Project

This directory contains the EMNLP/*ACL migration of the StructSynth paper.
It keeps the LaTeX source flat for Overleaf: `main.tex` is the main file at
the project root.

## Files

- `main.tex`: EMNLP/*ACL review-mode main file.
- `sections/`: migrated paper sections from the source version.
- `figures/`: figures used by the migrated paper.
- `references.bib`: project bibliography.
- `acl.sty` and `acl_natbib.bst`: official ACL style files.

## Build

From the project root:

```sh
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

For Overleaf, set `main.tex` as the main file.
