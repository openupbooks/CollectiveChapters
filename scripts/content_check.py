import sys, re, pathlib

BANNED = [
    r"(?i)\bexample-banned-phrase\b",
]

def scan_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    for pattern in BANNED:
        for m in re.finditer(pattern, text):
            start = max(0, m.start()-30)
            end = min(len(text), m.end()+30)
            hits.append((pattern, text[start:end].replace("\n", " ")))
    return hits

def main():
    docs = pathlib.Path("docs")
    failures = []
    for p in docs.rglob("*.md"):
        if p.name.startswith("_"):
            continue
        hits = scan_file(p)
        for pat, ctx in hits:
            failures.append(f"{p}: pattern `{pat}` → ...{ctx}...")
    if failures:
        print("🚫 Content check failed:")
        for f in failures:
            print("-", f)
        sys.exit(1)
    print("✅ Content check passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
