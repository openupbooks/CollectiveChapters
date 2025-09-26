import re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "questions"

FM_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)

def parse_front_matter(text):
    m = FM_RE.match(text)
    data = {}
    if m:
        fm = m.group(1)
        for line in fm.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def extract_quote(text):
    # Try "One-sentence wisdom" line first
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "One-sentence wisdom" in line:
            for j in range(i+1, len(lines)):
                val = lines[j].strip().strip("- ").strip()
                if val:
                    return val.strip('"')
    # Fallback: first blockquote
    for line in lines:
        if line.strip().startswith(">"):
            return line.strip().lstrip("> ").strip()
    return ""

def relpath(p):
    return p.relative_to(DOCS).as_posix()

def title_from_slug(slug):
    t = slug.replace("-", " ").strip()
    if not t: return slug
    return t[0].upper() + t[1:]

def build():
    DOCS.mkdir(parents=True, exist_ok=True)
    questions = collections.defaultdict(list)  # slug -> entries
    for md in DOCS.rglob("*.md"):
        if md.name == "index.md" or md.name.startswith("_"):
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        meta = parse_front_matter(text)
        quote = meta.get("summary") or extract_quote(text)
        meta["quote"] = quote
        meta["file"] = md.name
        parts = relpath(md).split("/")
        if len(parts) >= 2:
            qslug = parts[0]
            questions[qslug].append(meta)

    # Global questions index
    gl = ["# Questions", "", "A living atlas of global answers to shared philosophical questions.", ""]
    for qslug in sorted(questions.keys()):
        gl.append(f"- [{title_from_slug(qslug)}](./{qslug}/index.md)")
    (DOCS / "index.md").write_text("\n".join(gl) + "\n", encoding="utf-8")

    # Per-question index grouped by country
    for qslug, entries in questions.items():
        by_country = collections.defaultdict(list)
        for e in entries:
            by_country[e.get("country","Unknown")].append(e)

        lines = [f"# {title_from_slug(qslug)}", "", "Contributions grouped by country.", ""]
        for country in sorted(by_country.keys()):
            lines.append(f"## {country}")
            for e in sorted(by_country[country], key=lambda x: x.get("author","")):
                meta = []
                if e.get("religion"): meta.append(f"Religion: {e['religion']}")
                if e.get("language"): meta.append(f"Language: {e['language']}")
                meta_line = " · ".join(meta)
                lines.append(f"- [{e.get('author','Unknown')}]({e['file']})  ")
                if meta_line:
                    lines.append(f"  *{meta_line}*  ")
                if e.get("quote"):
                    lines.append(f"  > *{e['quote']}*  ")
            lines.append("")

        qdir = DOCS / qslug
        qdir.mkdir(parents=True, exist_ok=True)
        (qdir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == '__main__':
    build()
    print("Indexes generated.")
