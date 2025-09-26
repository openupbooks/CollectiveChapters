# scripts/generate_indexes.py
# Builds:
# - docs/chapters/index.md (list of topics)
# - docs/chapters/<topic>/index.md (grouped by country + "Add your chapter" button)
# - docs/pages/contributors.md (all author names)

import os
import re
import pathlib
import collections
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHAP = ROOT / "docs" / "chapters"
PAGES = ROOT / "docs" / "pages"

# Set your repo here, or override via env REPO_SLUG="owner/repo"
REPO_SLUG = os.getenv("REPO_SLUG", "openupbooks/collectivechapters")

FM_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)

def parse_front_matter(text: str) -> dict:
    """Very small YAML-ish parser (enough for simple key: value lines)."""
    m = FM_RE.match(text)
    data = {}
    if m:
        fm = m.group(1)
        for line in fm.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def extract_quote(text: str) -> str:
    """Try to pull a nice one-liner from 'One-sentence wisdom' or first blockquote."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "One-sentence wisdom" in line:
            for j in range(i + 1, len(lines)):
                val = lines[j].strip().strip("- ").strip()
                if val:
                    return val.strip('"')
    for line in lines:
        if line.strip().startswith(">"):
            return line.strip().lstrip("> ").strip()
    return ""

def human_title(slug: str) -> str:
    """Pretty title from slug; add '?' for 'What is ...' topics."""
    t = slug.replace("-", " ").title()
    if t.lower().startswith("what is "):
        t += "?"
    return t

def build():
    CHAP.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)

    topics: dict[str, list[dict]] = {}
    contributors: set[str] = set()

    # Collect all chapters
    for md in CHAP.rglob("*.md"):
        if md.name in ("index.md",) or md.name.startswith("_"):
            continue
        rel = md.relative_to(CHAP).as_posix()
        parts = rel.split("/")
        if len(parts) < 2:
            continue  # must be chapters/<topic>/<file>.md
        slug = parts[0]
        text = md.read_text(encoding="utf-8", errors="ignore")
        meta = parse_front_matter(text)
        meta["file"] = md.name
        meta["quote"] = meta.get("summary") or extract_quote(text)
        topics.setdefault(slug, []).append(meta)
        author = meta.get("author")
        if author:
            contributors.add(author)

    # Build main Chapters index
    chapters_index = ["# Chapters", "", "Browse topics by collected chapters.", ""]
    for slug in sorted(topics.keys()):
        chapters_index.append(f"- [{human_title(slug)}](./{slug}/index.md)")
    (CHAP / "index.md").write_text("\n".join(chapters_index) + "\n", encoding="utf-8")

    # Per-topic index (grouped by country) + CTA button
    for slug, entries in topics.items():
        by_country = collections.defaultdict(list)
        for e in entries:
            by_country[e.get("country", "Unknown")].append(e)

        title = human_title(slug)
        issue_title = urllib.parse.quote_plus(f"Chapter: {title}")
        issue_url = (
            f"https://github.com/{REPO_SLUG}/issues/new"
            f"?template=submit-chapter.yml&title={issue_title}&labels=chapter-submission"
        )

        lines = [
            f"# {title}",
            "",
            # Material for MkDocs button styling (needs 'attr_list' markdown extension)
            f"[➕ Add your chapter]({issue_url})" + " { .md-button .md-button--primary }",
            "",
            "Contributions grouped by country.",
            ""
        ]

        for country in sorted(by_country.keys()):
            lines.append(f"## {country}")
            # Sort within country by author
            for e in sorted(by_country[country], key=lambda x: x.get("author", "")):
                bits = []
                if e.get("religion"):
                    bits.append(f"Religion: {e['religion']}")
                if e.get("language"):
                    bits.append(f"Language: {e['language']}")
                meta_line = " · ".join(bits)

                # Link points to the file (we're inside chapters/<slug>/index.md)
                lines.append(f"- [{e.get('author','Unknown')}]({e['file']})  ")
                if meta_line:
                    lines.append(f"  *{meta_line}*  ")
                if e.get("quote"):
                    lines.append(f"  > *{e['quote']}*  ")
            lines.append("")

        tdir = CHAP / slug
        tdir.mkdir(parents=True, exist_ok=True)
        (tdir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # All contributors page
    clines = ["# All contributors", "", "People who have contributed chapters.", ""]
    for name in sorted(contributors):
        clines.append(f"- {name}")
    (PAGES / "contributors.md").write_text("\n".join(clines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    build()
    print("Indexes and contributors page generated.")
