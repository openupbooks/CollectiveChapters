# scripts/generate_indexes.py
# Builds:
# - docs/chapters/index.md (card grid of topics + "Add your chapter" buttons)
# - docs/chapters/<topic>/index.md (grouped by country + button)
# - docs/pages/contributors.md (authors + country/language badges)

import os
import re
import pathlib
import collections
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHAP = ROOT / "docs" / "chapters"
PAGES = ROOT / "docs" / "pages"

# set via env if needed: REPO_SLUG="owner/repo"
REPO_SLUG = os.getenv("REPO_SLUG", "openupbooks/collectivechapters")

FM_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def parse_front_matter(text: str) -> dict:
    m = FM_RE.match(text)
    data = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def extract_quote(text: str) -> str:
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
    t = slug.replace("-", " ").title()
    if t.lower().startswith("what is "):
        t += "?"
    return t


def build():
    CHAP.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)

    topics: dict[str, list[dict]] = {}
    contributors: dict[str, dict] = {}

    # include empty topic folders
    for p in CHAP.glob("*"):
        if p.is_dir() and not p.name.startswith("_"):
            topics.setdefault(p.name, [])

    # scan chapter files
    for md in CHAP.rglob("*.md"):
        if md.name == "index.md" or md.name.startswith("_"):
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

        author = (meta.get("author") or "").strip()
        country = (meta.get("country") or "").strip()
        lang = (meta.get("language") or "").strip()
        if author:
            entry = contributors.setdefault(author, {"countries": set(), "languages": set()})
            if country:
                entry["countries"].add(country)
            if lang:
                entry["languages"].add(lang)

    # ---- Chapters grid (cards) ----
    grid = ["# Chapters", "", "Browse topics by collected chapters.", "", '<div class="cc-grid">']
    for slug in sorted(topics.keys()):
        entries = topics[slug]
        n = len(entries)
        countries = sorted({(e.get("country") or "Unknown") for e in entries}) if n else []
        ttitle = human_title(slug)
        teaser = ""
        for e in entries:
            if e.get("quote"):
                teaser = e["quote"]
                break
        if not teaser:
            teaser = "Be the first to contribute a chapter."

        issue_title = urllib.parse.quote_plus(f"Chapter: {ttitle}")
        issue_url = (
            f"https://github.com/{REPO_SLUG}/issues/new"
            f"?template=submit-chapter.yml&title={issue_title}&labels=chapter-submission"
        )

        grid += [
            '<div class="cc-card">',
            f'  <h3><a href="./{slug}/index.md">{ttitle}</a></h3>',
            f'  <p class="cc-meta">{n} chapter{"s" if n != 1 else ""}'
            + (f' • {len(countries)} countr{"ies" if len(countries) != 1 else "y"}' if n else '')
            + '</p>',
            f'  <p class="cc-quote">“{teaser}”</p>',
            '  <div class="cc-actions">',
            f'    <a class="md-button md-button--primary" data-cc-cta="add-chapter" data-cc-topic="{slug}" href="{issue_url}">Add your chapter</a>',
            f'    <a class="md-button" href="./{slug}/index.md">Read</a>',
            '  </div>',
            '</div>',
        ]
    grid.append("</div>")
    (CHAP / "index.md").write_text("\n".join(grid) + "\n", encoding="utf-8")

    # ---- Per-topic index (grouped by country) ----
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
            f"[➕ Add your chapter]({issue_url})" + " { .md-button .md-button--primary }",
            "",
            "Contributions grouped by country.",
            "",
        ]
        if not entries:
            lines += ["_No chapters yet. Be the first to add yours!_", ""]

        for country in sorted(by_country.keys()):
            lines.append(f"## {country}")
            for e in sorted(by_country[country], key=lambda x: x.get("author", "")):
                bits = []
                if e.get("religion"):
                    bits.append(f"Religion: {e['religion']}")
                if e.get("language"):
                    bits.append(f"Language: {e['language']}")
                meta_line = " · ".join(bits)
                lines.append(f"- [{e.get('author','Unknown')}]({e['file']})  ")
                if meta_line:
                    lines.append(f"  *{meta_line}*  ")
                if e.get("quote"):
                    lines.append(f"  > *{e['quote']}*  ")
            lines.append("")

        tdir = CHAP / slug
        tdir.mkdir(parents=True, exist_ok=True)
        (tdir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- All contributors ----
    clines = ["# All contributors", "", "People who have contributed chapters.", ""]
    for name in sorted(contributors.keys()):
        entry = contributors[name]
        c_badges = " ".join([f'<span class="cc-badge">{c}</span>' for c in sorted(entry["countries"])]) or ""
        l_badges = " ".join([f'<span class="cc-badge">{l}</span>' for l in sorted(entry["languages"])]) or ""
        line = f"- {name}"
        extras = []
        if c_badges:
            extras.append(f'<span class="cc-badges">{c_badges}</span>')
        if l_badges:
            extras.append(f'<span class="cc-badges">{l_badges}</span>')
        if extras:
            line += " " + " ".join(extras)
        clines.append(line)
    (PAGES / "contributors.md").write_text("\n".join(clines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
    print("Indexes, topic pages, and contributors page generated.")
