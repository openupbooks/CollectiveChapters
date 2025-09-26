# Open Internet Book — Starter Kit (Questions + Auto-Index)

Open, curate, publish. Dit pakket bouwt automatisch een website én PDF, en genereert
indexpagina's per **vraag** met grouping op **land** (en metadata zoals taal/religie).

## Features
- **MkDocs + Material**: mooie openbare site + zoekfunctie.
- **PDF export**: `site/book.pdf` buildt automatisch op elke push naar `main`.
- **Auto-index**: `scripts/generate_indexes.py` scant `docs/questions/*` en maakt indexen.
- **Contributions**: 1 hoofdstuk = 1 MD-bestand; PR-flow met review.
- **Moderatie**: simpele content-check in CI, breidbaar.
- **Licentie**: standaard CC BY-SA 4.0.

## Mappen
```
docs/
  index.md                # home
  chapters/               # (optioneel) losse hoofdstukken buiten de vragenreeks
  questions/              # alle vragen + hoofdstukken per vraag
    _chapter-template.md  # template voor nieuwe inzendingen
    q1-what-is-truth/     # voorbeeldvraag met 2 bijdragen
scripts/
  content_check.py
  generate_indexes.py
```

## Workflow
1. Contributors voegen een MD-bestand toe in `docs/questions/<question-slug>/`.
2. CI draait `generate_indexes.py` → maakt/over schrijft `index.md` per vraag + `questions/index.md`.
3. CI bouwt site + PDF en deployt naar GitHub Pages.

Bekijk `CONTRIBUTING.md` voor de schrijf- en indienregels.
