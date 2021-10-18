#!/bin/bash

# Pass path to the directory with the jpegs you want to convert into svgs as an argument
if [[ $1 != "" ]]; then
  ext="*.jpeg"
  if [[ ${1: -1} != / ]]; then
    ext="/"$ext
  fi
  for f in $1$ext; do
    python3 "image_converter.py" "$f"
  done
else
  echo "Need to pass a file directory"
fi
