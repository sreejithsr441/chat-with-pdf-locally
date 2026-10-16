# Chat with your PDFs locally on Mac (private, no cloud)

Code for the Ring Zero video *Chat With Your PDFs Locally on Mac (Private, No Cloud)*. Ask your own PDFs questions with the
Wi-Fi off and get answers with page numbers. Everything runs through Ollama on your Mac; nothing is uploaded.

## Step 1 · The fastest way (no code)
Open the Ollama app, choose **continue locally** if it asks you to sign in, pick a model that runs on your Mac (not one
marked *cloud*), and drag in a short PDF such as `move-in-guide.pdf` (3 pages).

## Step 2 · Install the two models and pypdf
```bash
./setup.sh          # python3 -m pip install pypdf · ollama pull embeddinggemma-2:270m · ollama pull qwen3.5:9b
```
Less memory? Swap `qwen3.5:9b` for your pick from the "which model fits your Mac" video (edit `CHAT` in pdfchat.py).

## Step 3 · Index your PDF and ask
```bash
git clone https://github.com/sreejithsr441/chat-with-pdf-locally
cd chat-with-pdf-locally
python3 pdfchat.py sample.pdf --show          # prints the 5 passages it read, with scores and pages
```
Options: `--top 3` (read fewer passages) · `--ask "question"` (one question, then exit) ·
`--stuff --ctx 4096` (send the whole PDF instead of looking it up, to see the start get cut) ·
`--no-rules` (same model with no instructions, for comparison).

## Step 4 · Scanned PDFs: OCR first
```bash
python3 pdfchat.py sample-scanned.pdf         # stops: "No text found. This looks like a scanned PDF..."
brew install ocrmypdf
ocrmypdf sample-scanned.pdf sample-scanned-ocr.pdf
python3 pdfchat.py sample-scanned-ocr.pdf
```

## Check your context window
While a model is loaded: `ollama ps` and look under CONTEXT. Ollama's default depends on GPU memory
(under 24 GiB: 4K · 24–48 GiB: 32K · 48 GiB+: 256K, see https://docs.ollama.com/context-length).

## Files
| File | What it is |
| --- | --- |
| `pdfchat.py` | The script (156 lines): chunks of 900 characters with 150 overlap, kept per page; top 5 by cosine similarity; answers only from those passages, with page citations |
| `sample.pdf` | A 30-page **fictional** lease (Harbor Lane Properties). The landlord's name is on page 1 only; the notice clause is on page 23 |
| `sample-scanned.pdf` | The same lease as page images, with no text layer |
| `move-in-guide.pdf` | A 3-page guide for the drag-and-drop demo |
| `make_samples.py` | Rebuilds the three PDFs (needs reportlab and pymupdf) |
| `questions.txt` | The nine test questions |
| `results.csv` | My log: one row per question |
| `setup.sh` / `verify.sh` | Install, then a one-question check that an answer comes back with a page number |
| `TESTED.md` | Mac, macOS, Ollama version, models, context, date |

## Fixes
- **Wrong answers from a long PDF:** raise the context slider in Ollama's settings, or use the script. If it prints
  `Warning: prompt filled the window`, use `--top 3`.
- **"No text found":** it's a scan. Run `ocrmypdf` first.
- **`Error: model "..." not found` or `connection refused`:** open the Ollama app, then `ollama pull` both models again.
