#!/usr/bin/env bash

export VIRTUALENV='venv_lambda'
rm -fr $VIRTUALENV
# Setup fresh virtualenv and install requirements
virtualenv $VIRTUALENV
source $VIRTUALENV/bin/activate
pip install -r lambda_requirements.txt
deactivate

export VIRTUALENV='venv_lambda'
export ZIP_FILE='lambda.zip'
export PYTHON_VERSION='python3.6'
# Zip dependencies from virtualenv, and main.py
cd $VIRTUALENV/lib/$PYTHON_VERSION/site-packages/
zip -r9 ../../../../$ZIP_FILE *
cd ../../../../
zip -g $ZIP_FILE lambda_function.py