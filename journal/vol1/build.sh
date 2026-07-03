#!/usr/bin/env bash
# Compile every paper in vol1 with the shared PaMaBAI style.
set -e
cd "$(dirname "$0")"
export TEXINPUTS=".:../style:"
export BSTINPUTS=".:../style:"
export BIBINPUTS=".:../style:"
for d in 0*-*/; do
  ( cd "$d"
    pdflatex -interaction=nonstopmode paper.tex >/dev/null
    bibtex paper >/dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode paper.tex >/dev/null
    pdflatex -interaction=nonstopmode paper.tex >/dev/null
    echo "$d -> $(pdfinfo paper.pdf | awk '/^Pages/{print $2}') pages" )
done
