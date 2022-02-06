#!/usr/bin/env bash
set -eux

poetry run python -m translations.generate_po_file

export FIX_CORE_IMPORTS=1
export FIX_TESTS=1

for lang in es en
do
  export FUTURECODER_LANGUAGE=$lang
  poetry run python -m core.generate_static_files
  poetry run pytest tests/test_steps.py
done
