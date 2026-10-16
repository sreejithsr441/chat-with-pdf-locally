#!/usr/bin/env python3
"""pdfchat.py: ask your own PDF questions on your Mac, offline, with page numbers.

A small embedding model (the "librarian") finds the passages closest in meaning to your question;
the chat model (the "reader") answers only from those passages and cites the page.
Everything runs through Ollama on this machine. Nothing is uploaded.

  python3 pdfchat.py sample.pdf                  # index once, then ask in a loop
  python3 pdfchat.py sample.pdf --show           # also print the passages it read, with scores
  python3 pdfchat.py sample.pdf --top 3          # read fewer passages
  python3 pdfchat.py sample.pdf --ask "Who is the landlord?"   # one question, then exit
  python3 pdfchat.py sample.pdf --stuff --ctx 4096             # no lookup: send the whole PDF (to see truncation)
  python3 pdfchat.py sample.pdf --no-rules       # same model, no instructions (for comparison)
"""
import argparse, hashlib, json, math, os, re, sys, time, urllib.error, urllib.request
from pypdf import PdfReader

HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
HOST = HOST if HOST.startswith("http") else "http://" + HOST
EMBED, CHAT = "embeddinggemma-2:270m", "qwen3.5:9b"
CHUNK, OVERLAP = 900, 150                       # characters per passage, overlap between passages
Q_PREFIX = "task: question answering | query: "  # EmbeddingGemma 2 prefixes (model card)
D_PREFIX = "title: none | text: "
REFUSAL = "I can't find that in this document."
RULES = ["Answer only from the passages below.",
         "Cite the page for every fact, like [p. 4].",
         f"If the answer isn't there, say: {REFUSAL}"]


def post(path, payload, stream=False):
    req = urllib.request.Request(HOST + path, json.dumps(payload).encode(), {"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=600)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        if e.code == 404 or "not found" in msg:
            sys.exit(f'Error: model "{payload.get("model")}" not found. Pull it first:  ollama pull {payload.get("model")}')
        sys.exit(f"Error from Ollama ({e.code}): {msg}")
    except urllib.error.URLError:
        sys.exit(f"Error: can't reach Ollama at {HOST} (connection refused). Open the Ollama app, then try again.")
    if stream:
        return (json.loads(line) for line in r if line.strip())
    return json.loads(r.read())


def read_pages(pdf):
    out = []
    for i, page in enumerate(PdfReader(pdf).pages):
        out.append((i + 1, re.sub(r"\s+", " ", page.extract_text() or "").strip()))
    return out


def split(pages):
    chunks = []
    for num, text in pages:
        start = 0
        while start < len(text):
            chunks.append({"page": num, "text": text[start:start + CHUNK]})
            if start + CHUNK >= len(text):
                break
            start += CHUNK - OVERLAP
    return chunks


def embed(texts):
    vecs = []
    for i in range(0, len(texts), 32):
        res = post("/api/embed", {"model": EMBED, "input": texts[i:i + 32], "truncate": False})
        vecs += res["embeddings"]
    return [[x / (math.sqrt(sum(v * v for v in vec)) or 1) for x in vec] for vec in vecs]


def index(pdf, pages):
    key = hashlib.sha256(open(pdf, "rb").read()).hexdigest() + f"|{EMBED}|{CHUNK}|{OVERLAP}"
    path = pdf + ".index.json"
    if os.path.exists(path):
        cached = json.load(open(path))
        if cached.get("key") == key:
            print(f"Loaded index: {len(pages)} pages, {len(cached['chunks'])} chunks")
            return cached["chunks"]
    t0 = time.time()
    chunks = split(pages)
    for c, v in zip(chunks, embed([D_PREFIX + c["text"] for c in chunks])):
        c["vec"] = v
    json.dump({"key": key, "chunks": chunks}, open(path, "w"))
    print(f"Indexed {len(pages)} pages -> {len(chunks)} chunks in {time.time() - t0:.1f}s")
    return chunks


def context_size(ctx):
    if ctx:
        return ctx
    try:                                         # what Ollama actually loaded (same as `ollama ps` CONTEXT)
        req = urllib.request.urlopen(HOST + "/api/ps", timeout=5)
        for m in json.loads(req.read()).get("models", []):
            if m.get("name", "").startswith(CHAT.split(":")[0]) and m.get("context_length"):
                return m["context_length"]
    except Exception:
        pass
    return None


def ask(q, chunks, pages, a):
    if a.stuff:
        passages = [(n, t) for n, t in pages]
    else:
        qv = embed([Q_PREFIX + q])[0]
        scored = sorted(((sum(x * y for x, y in zip(qv, c["vec"])), c) for c in chunks), key=lambda s: -s[0])[:a.top]
        if a.show:
            for r, (s, c) in enumerate(scored, 1):
                print(f"  #{r}  score {s:.2f}  p. {c['page']}  {c['text'][:70]}…")
        passages = [(c["page"], c["text"]) for _, c in scored]
    body = "\n\n".join(f"[p. {n}] {t}" for n, t in passages) + f"\n\nQuestion: {q}"
    msgs = ([] if a.no_rules else [{"role": "system", "content": "\n".join(RULES)}]) + [{"role": "user", "content": body}]
    opts = {"temperature": 0}
    if a.ctx:
        opts["num_ctx"] = a.ctx
    used = 0
    for part in post("/api/chat", {"model": CHAT, "messages": msgs, "stream": True, "think": False, "options": opts}, stream=True):
        print(part.get("message", {}).get("content", ""), end="", flush=True)
        if part.get("done"):
            used = part.get("prompt_eval_count", 0)
    print()
    ctx = context_size(a.ctx)
    if ctx and used >= ctx - 32:
        print(f"Warning: prompt filled the window ({ctx} tokens). Try fewer passages: --top {max(1, a.top - 2)}")


def main():
    ap = argparse.ArgumentParser(description="Ask your PDF questions, offline, with page numbers.")
    ap.add_argument("pdf")
    ap.add_argument("--ask", help="ask one question and exit")
    ap.add_argument("--top", type=int, default=5, help="passages to read (default 5)")
    ap.add_argument("--show", action="store_true", help="print the passages it read, with scores")
    ap.add_argument("--ctx", type=int, help="context window for this run, e.g. 4096")
    ap.add_argument("--stuff", action="store_true", help="no lookup: send every page (shows truncation)")
    ap.add_argument("--no-rules", action="store_true", help="no instructions (for comparison)")
    a = ap.parse_args()
    pages = read_pages(a.pdf)
    if sum(len(t) for _, t in pages) < 20 * len(pages):
        base = os.path.splitext(a.pdf)[0]
        sys.exit(f"No text found. This looks like a scanned PDF. Run OCR first:  ocrmypdf {a.pdf} {base}-ocr.pdf")
    chunks = [] if a.stuff else index(a.pdf, pages)
    if a.ask:
        return ask(a.ask, chunks, pages, a)
    while True:
        try:
            q = input("Ask> ").strip()
        except (EOFError, KeyboardInterrupt):
            return print()
        if q:
            ask(q, chunks, pages, a)


if __name__ == "__main__":
    main()
