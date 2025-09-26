import os, pathlib, re, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHAP = ROOT / "docs" / "chapters"

def read(p): return pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")

def fm(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    data = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k,v = line.split(":",1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def list_topics():
    for p in CHAP.glob("*"):
        if p.is_dir() and not p.name.startswith("_"):
            yield p.name

def collect(slug):
    tdir = CHAP / slug
    items = []
    for md in sorted(tdir.glob("*.md")):
        if md.name == "index.md": continue
        meta = fm(read(md))
        items.append({"path": md, "meta": meta})
    items.sort(key=lambda x: (x["meta"].get("country","zzz"), x["meta"].get("author","zzz")))
    return items

def make_agg(slug):
    body = [f"# {slug.replace('-', ' ').title()} — Collected Chapters\n"]
    items = collect(slug)
    if not items:
        body.append("_No chapters yet._\n")
    for it in items:
        m = it["meta"]
        title = m.get("title","Chapter")
        author = m.get("author","Unknown")
        country = m.get("country","")
        lang = m.get("language","")
        rel = os.path.relpath(it["path"], start=ROOT / "docs")
        body.append(f"\n---\n\n## {author} ({country}) — *{title}*\n")
        if lang: body.append(f"*Language: {lang}*\n")
        body.append(f"\n[Original file]({rel})\n\n")
        txt = read(it["path"]); txt = re.sub(r"^---\n.*?\n---\n", "", txt, flags=re.DOTALL)
        body.append(txt.strip()+"\n")
    outdir = ROOT / "docs" / ".generated" / "books"
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{slug}.md"
    out.write_text("\n".join(body), encoding="utf-8")
    return out

def build_pdf(slug):
    import yaml, subprocess
    base = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))

    # ✅ make paths absolute so MkDocs doesn’t look under /tmp/
    base["docs_dir"] = str((ROOT / "docs").resolve())
    base["site_dir"] = str((ROOT / "site").resolve())

    agg = make_agg(slug)
    # keep the rest as is…

def add_links():
    for slug in list_topics():
        idx = CHAP / slug / "index.md"
        link = f"\n**Download as PDF:** [books/{slug}.pdf](../../books/{slug}.pdf)\n"
        if idx.exists():
            txt = read(idx)
            if "Download as PDF" not in txt:
                with open(idx,"a",encoding="utf-8") as f: f.write("\n"+link)
        else:
            idx.parent.mkdir(parents=True, exist_ok=True)
            idx.write_text(f"# {slug.replace('-', ' ').title()}\n\n{link}", encoding="utf-8")

def main():
    for slug in list_topics():
        build_pdf(slug)
    add_links()
    print("Per-topic PDFs built.")

if __name__ == "__main__":
    main()
