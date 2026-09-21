import { test } from 'node:test';
import assert from 'node:assert/strict';
import { countWordsToThesis } from './validate-content.js';

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
