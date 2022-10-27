#!/bin/bash

for pdfile in *.pdf ; do
  convert -verbose -density 500 -resize '800' -alpha opaque  "${pdfile}" "${pdfile%.*}".png
done

