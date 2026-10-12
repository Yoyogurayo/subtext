# subtext

Context-aware localization pipeline for indie games — JP↔EN first. Powered by Claude.

Machine translation fails on games because strings arrive without context: pronouns, character voice, item names, UI constraints. `subtext` keeps the **whole script in-context** — glossary, character voice sheets, and the full script — so every string comes out consistent. Ambiguities come back as questions for the writer instead of silent guesses.

## How it works

```
strings.csv (id, speaker, ja)
glossary.json (term -> canon translation)
characters.json (per-character voice sheet)
        |
        v
  single Claude pass  →  strings.en.csv + questions.json
```

One prompt holds the entire context, the way a human localizer would want it. This is the core of the product — see the roadmap for where it goes next.

## Quickstart

```bash
pip install -r requirements.txt

# preview the assembled context (no API key needed)
python -m subtext.translate data/ --dry-run

# run a real translation pass
export ANTHROPIC_API_KEY=...
python -m subtext.translate data/ -o out/
# → out/strings.en.csv, out/questions.json
```

## Status

Early development. Currently a CLI over the core pass; importers for Unity/Ren'Py and a review UI are on the roadmap. Piloting with indie devs and doujin circles in Tokyo — get in touch if you ship JP↔EN titles.

## Contact

Subtext — an independent project, Tokyo.
