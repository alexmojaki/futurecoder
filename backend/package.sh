#!/bin/bash

set -eux

rm -f package.zip
SITE_PACKAGES=$(python -c "from core.utils import site_packages; print(site_packages)")
CORE_IMPORTS=$(python -m core.core_imports)
pushd $SITE_PACKAGES
rm -f package.zip
zip -q -r package.zip $CORE_IMPORTS -x '*.pyc' -x '*__pycache__*' -x 'pygments/lexers*' -x '*friendly/locales*'
zip -q package.zip pygments/lexers/__init__.py pygments/lexers/_mapping.py pygments/lexers/python.py
popd

mv $SITE_PACKAGES/package.zip .
zip -q -r package.zip core -x '*.pyc' -x '*__pycache__*'
ls -alh package.zip
mv package.zip main/static/
