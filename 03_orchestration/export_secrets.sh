#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="${PWD}/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found in $(pwd)" >&2
  exit 1
fi

encode_and_export() {
  local key="$1"
  local value
  value=$(grep -E "^${key}=" "$ENV_FILE" | head -n1 | sed 's/^[^=]*=//; s/^"//; s/"$//')
  if [[ -z "$value" ]]; then
    echo "Warning: ${key} is empty or missing in .env, skipping" >&2
    return
  fi
  local encoded
  encoded=$(printf '%s' "$value" | base64 -w 0)
  export "SECRET_${key}=${encoded}"
  echo "Exported SECRET_${key}"
}

encode_and_export OPENAI_API_KEY
encode_and_export GEMINI_API_KEY
encode_and_export TAVILY_API_KEY
