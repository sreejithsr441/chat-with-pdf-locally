#!/usr/bin/env bash
# One-time setup on a Mac with the Ollama app installed and running.
set -euo pipefail
python3 -m pip install --upgrade pypdf
ollama pull embeddinggemma-2:270m     # the librarian: finds the passages (378 MB)
ollama pull qwen3.5:9b                # the reader: writes the answer (less RAM? use your pick from the Oct 8 video)
echo "ready: python3 pdfchat.py sample.pdf"
