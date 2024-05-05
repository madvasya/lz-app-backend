#!/bin/sh

find ./app -name "*.py" | xargs black --line-length 79 --skip-magic-trailing-comma
