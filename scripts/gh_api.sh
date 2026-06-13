#!/usr/bin/env bash
# GitHub API helper using curl (more reliable on Windows/MSYS)
# Usage: gh_api.sh <method> <path> [json_body]

TOKEN=$(python3 -c "
with open(r'C:\\Users\\Link\\Team\\Desktop\\.github_token') as f:
    print(f.read().strip())
")

METHOD="${1:-GET}"
PATH="$2"
BODY="${3:-}"

if [ -z "$PATH" ]; then
    echo "Usage: gh_api.sh <method> <path> [json_body]"
    exit 1
fi

if [ -n "$BODY" ]; then
    curl -s -X "$METHOD" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Content-Type: application/json" \
        -d "$BODY" \
        "https://api.github.com$PATH"
else
    curl -s -X "$METHOD" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com$PATH"
fi
