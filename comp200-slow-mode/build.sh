#!/bin/sh
# Assembles the single-file page from src/
cd "$(dirname "$0")"
{
  cat src/head.html
  cat src/body.html
  echo '<script>'
  cat src/core.js src/widgets.js src/data1.js src/data2.js src/data3.js src/data4.js src/app.js
  echo '</script>'
} > index.html
