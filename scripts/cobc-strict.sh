#!/usr/bin/env bash
# Compila con cobc y trata cualquier aviso como error.
set -eu
log=$(mktemp)
status=0
cobc "$@" >"$log" 2>&1 || status=$?
cat "$log"
if grep -E -i "warning:" "$log" >/dev/null; then
  echo "error: cobc produjo avisos" >&2
  rm -f "$log"
  exit 1
fi
rm -f "$log"
exit "$status"
