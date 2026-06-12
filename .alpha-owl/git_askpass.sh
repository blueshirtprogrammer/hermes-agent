#!/usr/bin/env bash
case "$1" in
  *Username*) printf '%s\n' 'blueshirtprogrammer' ;;
  *Password*) printf '%s\n' "$GITHUB_TOKEN" ;;
  *) printf '%s\n' "$GITHUB_TOKEN" ;;
esac
