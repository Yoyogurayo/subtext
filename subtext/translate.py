"""subtext translate — context-aware game string localization via Claude.

Reads a whole script plus glossary and character voice sheets, then asks
Claude to translate every string in a single pass — the same context a human
localizer would ask for, held in-context at once. Ambiguities come back as
questions for the writer instead of silent guesses.

Usage:
    python -m subtext.translate data/ -o out/            # full pass (needs ANTHROPIC_API_KEY)
    python -m subtext.translate data/ --dry-run          # print the prompt only
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

MODEL = os.environ.get("SUBTEXT_MODEL", "claude-sonnet-4-5")


def load_inputs(data_dir: Path):
    strings_path = data_dir / "strings.csv"
    glossary_path = data_dir / "glossary.json"
    characters_path = data_dir / "characters.json"
    if not strings_path.exists():
        sys.exit(f"missing {strings_path}")
    with strings_path.open(encoding="utf-8", newline="") as f:
        strings = list(csv.DictReader(f))
    glossary = json.loads(glossary_path.read_text(encoding="utf-8")) if glossary_path.exists() else {}
    characters = json.loads(characters_path.read_text(encoding="utf-8")) if characters_path.exists() else {}
    return strings, glossary, characters


def build_prompt(strings, glossary, characters, target: str) -> str:
    return f"""You are a professional game localizer (Japanese to {target}).

## Glossary — terms must always be translated exactly like this
{json.dumps(glossary, ensure_ascii=False, indent=2)}

## Character voice sheets — keep each speaker's register
{json.dumps(characters, ensure_ascii=False, indent=2)}

## Full script — translate every "ja" string, using the whole script as context
{json.dumps(strings, ensure_ascii=False, indent=2)}

Respond with JSON only:
{{
  "translations": [{{"id": "<string id>", "en": "<translation>"}}, ...],
  "questions": ["<any ambiguity a human writer should resolve, with suggested options>", ...]
}}"""


def run(data_dir: Path, out_dir: Path, target: str, dry_run: bool):
    strings, glossary, characters = load_inputs(data_dir)
    prompt = build_prompt(strings, glossary, characters, target)

    if dry_run:
        print(prompt)
        return

    import anthropic

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text
    result = json.loads(text[text.index("{"):text.rindex("}") + 1])

    out_dir.mkdir(parents=True, exist_ok=True)
    translated = {t["id"]: t["en"] for t in result["translations"]}
    with (out_dir / "strings.en.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "speaker", "en"])
        for row in strings:
            w.writerow([row["id"], row.get("speaker", ""), translated.get(row["id"], "")])
    (out_dir / "questions.json").write_text(
        json.dumps(result.get("questions", []), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {out_dir / 'strings.en.csv'} and {out_dir / 'questions.json'}")


def main():
    p = argparse.ArgumentParser(description="Context-aware game string localization via Claude.")
    p.add_argument("data_dir", type=Path, help="directory with strings.csv (+ glossary.json, characters.json)")
    p.add_argument("-o", "--out", type=Path, default=Path("out"))
    p.add_argument("--target", default="English")
    p.add_argument("--dry-run", action="store_true", help="print the assembled prompt without calling the API")
    args = p.parse_args()
    run(args.data_dir, args.out, args.target, args.dry_run)


if __name__ == "__main__":
    main()
