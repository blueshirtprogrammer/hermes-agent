#!/usr/bin/env bash
# GitHub token reader for Hermes Agent
# Reads token from secure file and outputs it
python3 -c "
with open(r'C:\Users\Link Team\Desktop\.github_token') as f:
    print(f.read().strip())
"