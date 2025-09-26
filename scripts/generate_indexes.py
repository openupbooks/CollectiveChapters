import re, pathlib, collections, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHAP = ROOT / "docs" / "chapters"
PAGES = ROOT / "docs" / "pages"

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
    # Try "One-sentence wisdom"
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

def build():
    CHAP.mkdir(parents=True, exist_ok=True)
    topics = {}  # slug -> list of entries
    contributors = set()

    for md in CHAP.rglob("*.md"):
        if md.name in ("index.md",) or md.name.startswith("_"):
            continue
        rel = md.relative_to(CHAP).as_posix()
        parts = rel.split("/")
        if len(parts) < 2:
            continue
        slug = parts[0]
        text = md.read_text(encoding="utf-8", errors="ignore")
        meta = parse_front_matter(text)
        meta["file"] = md.name
        meta["quote"] = meta.get("summary") or extract_quote(text)
        topics.setdefault(slug, []).append(meta)
        if meta.get("author"):
            contributors.add(meta["author"])

    # Build chapters/index.md (list of topics)
    idx = ["# Chapters", "", "Browse topics by collected chapters.", ""]
    for slug in sorted(topics.keys()):
        idx.append(f"- [{slug.replace('-', ' ').title()}](./{slug}/index.md)")
    (CHAP / "index.md").write_text("\n".join(idx) + "\n", encoding="utf-8")

    # Per-topic index grouped by country
    for slug, entries in topics.items():
        by_country = collections.defaultdict(list)
        for e in entries:
            by_country[e.get("country","Unknown")].append(e)
        lines = [f"# {slug.replace('-', ' ').title()}", "", "Contributions grouped by country.", ""]
        for country in sorted(by_country.keys()):
            lines.append(f"## {country}")
            for e in sorted(by_country[country], key=lambda x: x.get("author","")):
                meta_bits = []
                if e.get("religion"): meta_bits.append(f"Religion: {e['religion']}")
                if e.get("language"): meta_bits.append(f"Language: {e['language']}")
                meta_line = " · ".join(meta_bits)
                lines.append(f"- [{e.get('author','Unknown')}]({e['file']})  ")
                if meta_line:
                    lines.append(f"  *{meta_line}*  ")
                if e.get("quote"):
                    lines.append(f"  > *{e['quote']}*  ")
            lines.append("")
        tdir = CHAP / slug
        tdir.mkdir(parents=True, exist_ok=True)
        (tdir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Build All Contributors page
    PAGES.mkdir(parents=True, exist_ok=True)
    clines = ["# All contributors", "", "People who have contributed chapters.", ""]
    for name in sorted(contributors):
        clines.append(f"- {name}")
    (PAGES / "contributors.md").write_text("\n".join(clines) + "\n", encoding="utf-8")

if __name__ == '__main__':
    build()
    print("Indexes and contributors page generated.")
