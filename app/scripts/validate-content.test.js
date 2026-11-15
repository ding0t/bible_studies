import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { bareReferences, countWordsToThesis, isDraftFrontmatter, linksToDrafts } from './validate-content.js';

// Check 14 measures how long a study's opening makes a reader wait for its point, by finding
// the first bold run. The regex IS the check, and it shipped wrong: the inner class excluded
// every asterisk, so a bold thesis containing an italicised transliteration -- which this
// corpus writes constantly -- could not match at all.
//
// The failure mode is the reason these tests exist. It did not report "no thesis found". It
// fell through to the NEXT bold run further down the page and reported a plausible number
// measured from the wrong place, which no amount of staring at the corpus would reveal.
// A check that answers confidently and wrongly is worse than one that throws.

test('finds a plain bold thesis', () => {
  assert.equal(countWordsToThesis('one two three **the thesis** rest'), 3);
});

// The regression. Before the fix this returned Infinity here, and on a real page it returned
// the distance to whatever bold run came next.
test('finds a bold thesis containing italics', () => {
  assert.equal(countWordsToThesis('one two three **the verb is *qadash* here** rest'), 3);
});

test('finds a bold thesis that ends on an italic word', () => {
  assert.equal(countWordsToThesis('one two three **and it is *sanctify*** rest'), 3);
});

// Bold spans hard-wrapped lines constantly in this corpus. A pattern that stops at every
// newline under-reports badly -- it once read last-supper's thesis as 416 words in, not 180.
test('a bold run may cross a single newline', () => {
  assert.equal(countWordsToThesis('one two **a thesis spanning\na single newline** rest'), 2);
});

// ...but a blank line means the bold never closed, so this is not a thesis.
test('a blank line terminates the bold run', () => {
  assert.equal(countWordsToThesis('one two **not a thesis\n\nstill not** rest'), Infinity);
});

// The guard the old [^*\n] class was really there for: one run must not swallow the next.
test('stops at the first of two bold runs', () => {
  assert.equal(countWordsToThesis('**first** and later **second**'), 0);
});

test('reports Infinity when a study never states a point in bold', () => {
  assert.equal(countWordsToThesis('no bold anywhere in this opening at all'), Infinity);
});

// Headings are stripped before measuring, so a long ## line is not charged to the reader.
test('does not count heading text toward the toll', () => {
  assert.equal(countWordsToThesis('## A Heading With Several Words\n\none **thesis**'), 1);
});

// Word counting requires a letter, so verse numbers and bare punctuation are not words.
test('counts only tokens containing a letter', () => {
  assert.equal(countWordsToThesis('13 14 -- one **thesis**'), 1);
});

// Importing this module must do no I/O. It used to run `git log` over the whole content
// history at module scope for check 17, so importing one pure helper spawned git and made the
// import depend on being inside a checkout. Guarded by putting a fake `git` first on PATH and
// asserting it is never reached -- which is stronger than counting execFileSync calls, since
// it does not depend on whether a monkeypatch reaches an ESM module's live bindings.
test('importing the module spawns no subprocess', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'vc-import-'));
  const marker = path.join(dir, 'git-was-called');
  // Exits non-zero on purpose: lastCommitDates() already tolerates git failing, so the only
  // thing under test is whether it was invoked at all.
  fs.writeFileSync(path.join(dir, 'git'), `#!/bin/sh\ntouch "${marker}"\nexit 1\n`, { mode: 0o755 });

  const moduleUrl = pathToFileURL(path.join(import.meta.dirname, 'validate-content.js')).href;
  execFileSync(process.execPath, ['-e', `import(${JSON.stringify(moduleUrl)})`], {
    env: { ...process.env, PATH: `${dir}${path.delimiter}${process.env.PATH}` },
  });

  assert.equal(
    fs.existsSync(marker),
    false,
    'importing validate-content.js spawned git -- check 17 is computing at module scope again'
  );
});

test('linksToDrafts finds relative links to draft pages, by file, anchor and directory', () => {
  const dir = '/site/last-things';
  const drafts = new Set(['/site/last-things/end-of-the-age.md', '/site/salvation/index.md']);
  const body = [
    'See [the end](end-of-the-age.md#the-end-has-already-come) and [again](end-of-the-age.md).',
    'A section [landing](../salvation/) and a published [page](rapture.md).',
    'Outside links are ignored: [web](https://example.com/end-of-the-age.md).',
    '```',
    '[in a code fence](end-of-the-age.md)',
    '```',
  ].join('\n');
  assert.deepEqual(linksToDrafts(body, dir, drafts), [
    'end-of-the-age.md#the-end-has-already-come',
    'end-of-the-age.md',
    '../salvation/',
  ]);
});

test('isDraftFrontmatter accepts true bare or quoted, as hooks/draft_pages.py does', () => {
  assert.equal(isDraftFrontmatter('title: "x"\ndraft: true'), true);
  assert.equal(isDraftFrontmatter('draft: "true"'), true);
  assert.equal(isDraftFrontmatter('draft: false'), false);
});

// Check 26: bare references. What it must catch, and each kind of thing it must leave alone.
const bare = (md) => bareReferences(md).map((b) => b.ref);

test('flags a stand-alone bare reference', () => {
  assert.deepEqual(bare('She touches (5:27) the fringe.'), ['5:27']);
  assert.deepEqual(bare('The verb returns at 4:16 in the next scene.'), ['4:16']);
});

test('reports only the first of a bare run', () => {
  assert.deepEqual(bare('He does it at 1:22, 2:15, 2:17 and 4:14.'), ['1:22']);
});

test('a continuation of a named reference is fine', () => {
  assert.deepEqual(bare('The bride (Revelation 21:2, 9; 22:17) is ready.'), []);
  assert.deepEqual(bare('As the hypocrites do (Matthew 6:2, ESV; 6:5, 16).'), []);
});

test('a book named in words just before is fine, as the pop-up reads it', () => {
  assert.deepEqual(bare('The sons of God appear both in Job (1:6; 2:1).'), []);
});

test('a new sentence does not inherit the last one\'s book', () => {
  assert.deepEqual(bare('Jesus speaks (John 4:10). Later the woman runs (4:28).'), ['4:28']);
});

test('leaves quotations, headings, alt text and inline code alone', () => {
  assert.deepEqual(bare('> 3 Why do you see (7:3) the speck'), []);
  assert.deepEqual(bare('## The Faithful Servant (24:45-51)'), []);
  assert.deepEqual(bare('[![Panel 1 (5:27): she reaches](a.svg)](a.svg)'), []);
  assert.deepEqual(bare('The note lists "the themes (90:1-2, 4)" in Book IV.'), []);
  assert.deepEqual(bare('Never write a bare `(21:2)` in a study.'), []);
});

test('leaves non-biblical works, credits and times alone', () => {
  assert.deepEqual(bare('R. H. Charles, trans., *The Book of Enoch* (1912), 16:1.'), []);
  assert.deepEqual(bare("Tobit's exiles are in Nineveh (1:2)."), []);
  assert.deepEqual(bare('"Sanctified, sanctified" (2:7, trans. Kulp).'), []);
  assert.deepEqual(bare('The sun set at 6:20pm that day.'), []);
});

test('a table cell follows its header and the rows above it', () => {
  assert.deepEqual(bare('| Matthew 24 | Mark 13 |\n|---|---|\n| 24:3 | 13:3 |'), []);
  assert.deepEqual(bare('| Verse | Word |\n|---|---|\n| John 4:6 | spring |\n| 4:11 | shaft |'), []);
  assert.deepEqual(bare('| Verse | Word |\n|---|---|\n| 4:11 | shaft |'), ['4:11']);
});
