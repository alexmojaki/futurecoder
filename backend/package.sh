#!/bin/bash

set -eux

ZIP_PATH=`pwd`/main/static/package.zip
rm -f $ZIP_PATH

SITE_PACKAGES=$(python -c "from core.utils import site_packages; print(site_packages)")
CORE_IMPORTS=$(python -m core.core_imports)
pushd $SITE_PACKAGES
zip -q -r $ZIP_PATH $CORE_IMPORTS -x '*.pyc' -x '*__pycache__*' -x 'pygments/lexers*' -x '*friendly/locales*' -x '*birdseye/static*'
zip -q $ZIP_PATH pygments/lexers/__init__.py pygments/lexers/_mapping.py pygments/lexers/python.py
popd

zip -q -r $ZIP_PATH core -x '*.pyc' -x '*__pycache__*'
ls -alh $ZIP_PATH
