# Open Internet Book — Starter Kit (Questions + Auto-Index)

An open, curated book project. This starter builds a public website and a single PDF,
and auto-generates index pages per **question**, grouped by **country** with useful metadata.

## Features
- **MkDocs + Material**: fast public website with search.
- **Automatic PDF export**: `site/book.pdf` on every push to `main`.
- **Auto-index generator**: scans `docs/questions/*` and creates index pages.
- **Contributions via PRs**: one chapter = one Markdown file; review required.
- **Moderation check**: simple content checker in CI (expand as you wish).
- **License**: Creative Commons **CC BY-SA 4.0** by default.

## Structure
```
docs/
  index.md                 # homepage
  chapters/                # optional area for non-question chapters
  questions/               # questions + chapters per question
    _chapter-template.md   # contributor template
    q1-what-is-truth/      # example question with 2 sample chapters
scripts/
  content_check.py
  generate_indexes.py
```

## Workflow
1. Contributors add a Markdown file under `docs/questions/<question-slug>/`.
2. CI runs `scripts/generate_indexes.py` to build `questions/index.md` and per-question indexes.
3. CI builds the site + PDF and deploys to GitHub Pages.

See `CONTRIBUTING.md` for writing and submission guidelines.
