#!/usr/bin/env bash
# GitHub API helper for Hermes Agent fork
# Usage: github_api.sh <endpoint> [method] [body]
# Reads token from ~/.github_token securely via Python

TOKEN=$(python3 -c "
with open(r'C:\Users\Link Team\Desktop\.github_token') as f:
    print(f.read().strip())
")

METHOD="${2:-GET}"
ENDPOINT="$1"
BODY="${3:-}"

if [ -n "$BODY" ]; then
    curl -s -X "$METHOD" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Content-Type: application/json" \
        -d "$BODY" \
        "https://api.github.com$ENDPOINT"
else
    curl -s -X "$METHOD" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com$ENDPOINT"
fi
