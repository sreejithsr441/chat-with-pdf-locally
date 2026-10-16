#!/usr/bin/env bash
# Asks question 1 and checks that an answer with a page number comes back.
set -euo pipefail
cd "$(dirname "$0")"
out=$(python3 pdfchat.py sample.pdf --ask "How much notice do I need to give to end the lease?")
echo "$out"
echo "$out" | grep -Eq '\[p\. ?[0-9]+\]' && echo "OK: answer cites a page" || { echo "FAIL: no page number in the answer"; exit 1; }
