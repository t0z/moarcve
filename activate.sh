#!/usr/bin/bash

if [ ! -d env3 ]; then
    make venv
fi
source env3/bin/activate
