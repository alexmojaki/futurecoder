#!/bin/bash

set -eux

ZIP_PATH=`pwd`/main/static/package.zip
rm -f $ZIP_PATH

SITE_PACKAGES=$(python -c "from core.utils import site_packages; print(site_packages)")

if ! diff core/core_imports.txt <(python -m core.core_imports)
  then
  set +eux
  echo "You need to update core_imports.txt:"
  echo "python -m core.core_imports > core/core_imports.txt"
  exit 1
fi

CORE_IMPORTS=$(cat core/core_imports.txt)

pushd $SITE_PACKAGES
zip -q -r $ZIP_PATH $CORE_IMPORTS -x '*.pyc' -x '*__pycache__*' -x 'pygments/lexers*' -x '*friendly/locales*' -x '*birdseye/static*'
zip -q $ZIP_PATH pygments/lexers/__init__.py pygments/lexers/_mapping.py pygments/lexers/python.py
popd

zip -q -r $ZIP_PATH core -x '*.pyc' -x '*__pycache__*'
ls -alh $ZIP_PATH
