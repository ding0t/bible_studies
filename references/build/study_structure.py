#!/usr/bin/env python3
"""Structure measurements for the read-bible-study skill: outline, prose-identity, corpus survey.

Why these three live together
-----------------------------
read-bible-study restructures a study without changing a sentence. Two of its phases were shell
incantations, and both were doing the wrong amount of work:

- **Phase 2 (measure)** ran `npm run validate` -- all 21 checks across 86 files -- to learn the
  section sizes of one file, and only ever saw Check 21's >600-word tail. The skill's actual
  target is 250-400 words between headings, which nothing reported.
- **Phase 4 (verify nothing but structure changed)** was a four-line pipeline through temp files.
  That is the check the whole pass rests on: if it is wrong, a prose edit ships inside a
  "structure only" commit and nobody re-verifies the study. A check that important should not be
  retyped from memory each time.

`prose_words` is deliberately the same rule the validator's Check 21 uses -- tables, lists, block
quotes and fenced code excluded -- so the tool and the check can never disagree about what a
600-word section is.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = REPO_ROOT / "docs" / "content"

TARGET_MIN, TARGET_MAX = 250, 400   # the skill's aspiration; p75-p88 of this corpus
WARN_AT = 600                       # validator Check 21; p96, the far tail

_HEADING = re.compile(r"^(#{2,4})\s+(.*)$")
_LIST_ITEM = re.compile(r"^([-*+]\s|\d+\.\s)")


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def _prose_lines(lines: list[str]) -> list[str]:
    """Only lines a reader reads as continuous prose.

    Tables, lists and block quotes are already visually broken -- a long reference table is not a
    wall -- and fenced code is not prose at all. Same rule as validate-content.js Check 21.
    """
    out, in_fence = [], False
    for line in lines:
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not s:
            continue
        if s.startswith("|") or s.startswith(">") or _LIST_ITEM.match(s):
            continue
        out.append(s)
    return out


def _resolve(path: str) -> pathlib.Path:
    p = pathlib.Path(path)
    for candidate in (REPO_ROOT / p, CONTENT_DIR / p, p):
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"no such study: {path}")


def _sections(text: str) -> list[dict]:
    lines = _strip_frontmatter(text).splitlines()
    sections, current, heading, level, start = [], [], None, 0, 0
    for i, line in enumerate(lines, 1):
        m = _HEADING.match(line.strip())
        if m:
            if heading is not None:
                sections.append({"heading": heading, "level": level, "line": start,
                                 "words": len(" ".join(_prose_lines(current)).split())})
            heading, level, start, current = m.group(2).strip(), len(m.group(1)), i, []
            continue
        current.append(line)
    if heading is not None:
        sections.append({"heading": heading, "level": level, "line": start,
                         "words": len(" ".join(_prose_lines(current)).split())})
    return sections


def outline(path: str) -> dict:
    """Section-by-section prose measurements for one study.

    `verdict` per section: ok | long (over the 400-word target) | wall (over 600, Check 21 fires).
    """
    file = _resolve(path)
    sections = _sections(file.read_text(encoding="utf-8", errors="replace"))
    body = [s for s in sections if s["words"] > 0]
    for s in sections:
        s["verdict"] = ("wall" if s["words"] > WARN_AT
                        else "long" if s["words"] > TARGET_MAX else "ok")
    counts = sorted(s["words"] for s in body)
    return {
        "file": str(file.relative_to(REPO_ROOT)),
        "sections": sections,
        "summary": {
            "sections": len(sections),
            "with_prose": len(body),
            "median_words": counts[len(counts) // 2] if counts else 0,
            "longest_words": counts[-1] if counts else 0,
            "over_target": sum(1 for w in counts if w > TARGET_MAX),
            "walls": sum(1 for w in counts if w > WARN_AT),
            "target": f"{TARGET_MIN}-{TARGET_MAX} words between headings",
        },
    }


def _prose_diff(before: str, after: str) -> dict:
    """Compare two versions of a file's text at the prose level -- the comparison `prose_identity`
    runs between disk and a git ref, factored out so it can also run ref-to-ref (see
    test_study_structure.py's use of this against two fixed historical commits, rather than one
    fixed commit and a working tree that later, unrelated edits can and did move out from under
    it)."""

    def prose_set(text: str) -> list[str]:
        # Frontmatter is not prose. Comparing it made date_modified -- which
        # refresh_frontmatter_provenance.py rewrites on every run -- look like a deleted sentence,
        # which is the one finding this check treats as always a defect. A verifier that cries
        # wolf on a routine edit is a verifier people stop reading.
        body = _strip_frontmatter(text)
        return _prose_lines([l for l in body.splitlines() if not _HEADING.match(l.strip())])

    from collections import Counter
    old_c, new_c = Counter(prose_set(before)), Counter(prose_set(after))
    removed = sorted((old_c - new_c).elements())
    added = sorted((new_c - old_c).elements())

    def allowed(line: str) -> bool:
        """The summary line is the pass's one permitted addition. Frontmatter never reaches here."""
        return line.startswith("**In one sentence:**")

    unexpected = [l for l in added if not allowed(l)]
    return {
        "clean": not removed and not unexpected,
        "removed": removed,
        "added_allowed": [l for l in added if allowed(l)],
        "added_unexpected": unexpected,
        "verdict": (
            "no sentence changed" if not removed and not unexpected
            else "PROSE CHANGED -- revert the unexpected lines, or hand the file to "
                 "review-bible-study, because a structural pass no longer describes it"
        ),
        "note": ("A removal is always a defect: this pass has no operation that deletes a sentence."
                 if removed else None),
    }


def prose_identity(path: str, ref: str = "HEAD") -> dict:
    """Phase 4: prove the restructure changed no sentence.

    Compares the set of prose lines (headings and blanks excluded) against the same file at `ref`.
    Frontmatter is excluded on both sides, so provenance edits never register. A removal is always
    a defect -- the pass has no operation that deletes a sentence. The only permitted addition is
    the one-line summary; anything else is reported so the author can revert it rather than
    discovering it in review.
    """
    file = _resolve(path)
    rel = file.relative_to(REPO_ROOT).as_posix()
    try:
        before = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{ref}:{rel}"],
                                capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        return {"error": f"cannot read {rel} at {ref}: {e.stderr.strip()}"}

    return {"file": rel, "ref": ref,
            **_prose_diff(before, file.read_text(encoding="utf-8", errors="replace"))}


def survey(limit: int = 20, include_drafts: bool = False) -> dict:
    """Corpus mode: published studies ranked by their worst unbroken prose run.

    Nothing else owns these -- develop-bible-study only touches new content, and
    review-bible-study would charge a full verification pass to split a heading.
    """
    rows = []
    for file in sorted(CONTENT_DIR.rglob("*.md")):
        text = file.read_text(encoding="utf-8", errors="replace")
        if "commentary-index:auto-start" in text:
            continue
        draft = bool(re.search(r"^draft:\s*true", text, re.M))
        if draft and not include_drafts:
            continue
        sections = [s for s in _sections(text) if s["words"] > 0]
        if not sections:
            continue
        worst = max(sections, key=lambda s: s["words"])
        if worst["words"] <= WARN_AT:
            continue
        rows.append({
            "file": str(file.relative_to(CONTENT_DIR)),
            "draft": draft,
            "worst_section": worst["heading"],
            "worst_words": worst["words"],
            "walls": sum(1 for s in sections if s["words"] > WARN_AT),
            "over_target": sum(1 for s in sections if s["words"] > TARGET_MAX),
        })
    # Live pages outrank drafts: a reader is meeting them now.
    rows.sort(key=lambda r: (r["draft"], -r["worst_words"]))
    return {"files_needing_a_pass": len(rows), "ranked": rows[:limit],
            "note": "A live page a reader is meeting now outranks a draft."}


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", nargs="?", help="study path; omit for the corpus survey")
    ap.add_argument("--verify-against", metavar="REF",
                    help="also run the Phase 4 prose-identity check against this git ref")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    if not args.path:
        print(json.dumps(survey(args.limit), indent=2))
    else:
        out = {"outline": outline(args.path)}
        if args.verify_against:
            out["prose_identity"] = prose_identity(args.path, args.verify_against)
        print(json.dumps(out, indent=2, ensure_ascii=False))
