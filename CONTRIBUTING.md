# Contributing Guidelines

## How to contribute
- Create a branch and add your chapter under `docs/questions/<question-slug>/<your-file>.md`.
- Copy the template: `docs/questions/_chapter-template.md`.
- Submit a Pull Request (PR). One chapter per PR.

## Writing rules
- Include front matter: `title`, `author`, `country`, `language`, optional `religion`, optional `summary`.
- Primary language is English, but you may write in your own language **if you include a short English summary**.
- Be respectful; no hateful, harassing or doxxing content. Avoid plagiarism; cite your sources.
- Suggested length: 300–2000 words (not strict).

## Review & moderation
- PRs require maintainer approval before merging.
- CI runs a simple content check; offensive content may fail the build (see `scripts/content_check.py`).
