# Collective Chapters — Ultimate Starter

A production-ready starter for an open, curated book where anyone can contribute a chapter.

## Highlights
- **Public website** (MkDocs Material)
- **Auto indexes**: by topic under **Chapters**, grouped by **country**, showing **religion/language**
- **Per‑topic PDFs** (e.g. `/books/what-is-truth.pdf`) built from all chapters of that topic
- **PR workflow**: one chapter per PR, required review
- **Moderation**: simple content check script (customize)
- **Contributor templates**: PR template + Issue form (“Submit a chapter”)
- **License**: CC BY-SA 4.0 (content stays open)

## Structure
```
docs/
  index.md
  chapters/                 # topics (each topic is a "question")
    _chapter-template.md
    what-is-truth/
      amina-elkarim.md
      diego-alvarez.md
    what-is-love/           # (+ others created empty for you)
    what-is-happiness/
    what-is-life/
    what-is-friendship/
    what-is-time/
    what-is-justice/
    what-is-freedom/
    what-is-peace/
  pages/
    about.md
    contact.md
scripts/
  content_check.py
  generate_indexes.py       # builds chapters index and per-topic indexes + Contributors page
  build_topic_pdfs.py       # builds /books/<topic>.pdf
.github/
  workflows/build.yml
  pull_request_template.md
  ISSUE_TEMPLATE/submit-chapter.yml
CODE_OF_CONDUCT.md
CONTRIBUTING.md
LICENSE.md
mkdocs.yml
```

## Getting Started
1. Create a **public** repo and push these files to `main`.
2. **Settings → Pages → Source: GitHub Actions.**
3. **Settings → Actions → General → Workflow permissions: Read and write.**
4. Push a small change → check **Actions** → after a green run your site is live.
5. Navigation: Home / Chapters / About Project / All contributors / Contact.

### Per‑topic PDFs
The workflow builds `/books/<topic>.pdf` (e.g., `/books/what-is-truth.pdf`) that concatenates all chapters for that topic. There is **no global PDF** in this setup.

### GA4
In `mkdocs.yml` set your property in:
```
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

### Branch Protection (moderation)
- **Settings → Branches → Add rule** for `main`:
  - Require a pull request before merging (min **1 approval**)
  - Require status checks to pass (**Build & Deploy**)
