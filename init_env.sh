#!/usr/bin/env bash
# Loads variables from .env into the current shell environment.
# Portable across macOS (bash 3.2) and Ubuntu Linux.
# Usage: source ./init_env.sh   (must be sourced, not executed, to export into your shell)

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: env file '$ENV_FILE' not found." >&2
    return 1 2>/dev/null || exit 1
fi

set -a  # auto-export all variables sourced below
# shellcheck disable=SC1090
source <(grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$' | sed -e 's/[[:space:]]*$//')
set +a

echo "Environment variables loaded from $ENV_FILE:"
grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$' | cut -d '=' -f1
