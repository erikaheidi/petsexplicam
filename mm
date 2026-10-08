#!/bin/sh
# Roda o moviemakr sempre contra ESTE workspace, independente do
# $MOVIEMAKR_WORKSPACE global do shell (que aponta para ~/moviemakr-workspace).
#   ./mm render movies/<filme>/scripts/v1.yaml --dry-run
here=$(cd "$(dirname "$0")" && pwd)
MOVIEMAKR_HOME=${MOVIEMAKR_HOME:-$HOME/Projects/moviemakr}
MOVIEMAKR_WORKSPACE=$here exec "$MOVIEMAKR_HOME/.venv/bin/python" "$MOVIEMAKR_HOME/moviemakr.py" "$@"
