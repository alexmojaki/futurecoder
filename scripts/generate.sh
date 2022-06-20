#!/usr/bin/env bash
set -eux

# Generate various files, particularly for use in development.

poetry run python -m translations.generate_po_file

export FIX_CORE_IMPORTS=1  # update core_imports.txt in generate_static_files
export FIX_TESTS=1  # update tests/golden_files/$FUTURECODER_LANGUAGE/test_transcript.json in test_steps.py

for lang in ${FUTURECODER_LANGUAGES:-en}
do
  export FUTURECODER_LANGUAGE=$lang
  poetry run python -m scripts.generate_static_files
  poetry run pytest tests/test_steps.py
done
