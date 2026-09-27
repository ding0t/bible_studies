import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findRefs, findStrongs, formatRef, parseRef, resolveRelative } from './scriptureRefs.js';

const found = (text) => findRefs(text).map((r) => [text.slice(r.start, r.end).trim(), r.ref.book ? formatRef(r.ref) : `rel ${r.ref.v1}-${r.ref.v2}`]);

test('a verse, a range, a cross-chapter range and a whole chapter', () => {
  assert.deepEqual(found('See Romans 8:28 and Ruth 3:9-13, then Ruth 3:18-4:2 and Psalm 23.'), [
    ['Romans 8:28', 'Romans 8:28'],
    ['Ruth 3:9-13', 'Ruth 3:9–13'],
    ['Ruth 3:18-4:2', 'Ruth 3:18–4:2'],
    ['Psalm 23', 'Psalms 23'],
  ]);
});

test('numbered books, abbreviations and the ESV label after them', () => {
  assert.deepEqual(found('(1 Corinthians 13:4-7, ESV) and 2Pe 3:8 (ESV) and 1 Jn 4:8'), [
    ['1 Corinthians 13:4-7', '1 Corinthians 13:4–7'],
    ['2Pe 3:8', '2 Peter 3:8'],
    ['1 Jn 4:8', '1 John 4:8'],
  ]);
});

test('a reference broken across a line keeps working', () => {
  assert.deepEqual(found('Daniel\n9:27 (ESV)'), [['Daniel\n9:27', 'Daniel 9:27']]);
});

test('continuations inherit the book and, for a bare verse, the chapter', () => {
  assert.deepEqual(found('John 1:1, 14; 3:16-18 and Romans 8; 9'), [
    ['John 1:1', 'John 1:1'],
    ['14', 'John 1:14'],
    ['3:16-18', 'John 3:16–18'],
    ['Romans 8', 'Romans 8'],
    ['9', 'Romans 9'],
  ]);
});

test('a number that starts the next book is not a continuation', () => {
  assert.deepEqual(found('Luke 2:1, 2 Corinthians 5:17'), [
    ['Luke 2:1', 'Luke 2:1'],
    ['2 Corinthians 5:17', '2 Corinthians 5:17'],
  ]);
});

test('one-chapter books read the number as a verse', () => {
  assert.deepEqual(found('Jude 6 and Philemon 10-12'), [
    ['Jude 6', 'Jude 6'],
    ['Philemon 10-12', 'Philemon 10–12'],
  ]);
});

test('prose words and bare abbreviations are left alone', () => {
  assert.deepEqual(found('Mark 4 of the job 3 times, Ex 2, Is 5 and the Genesis account'), [['Mark 4', 'Mark 4']]);
});

test('relative verses resolve against the passage in hand', () => {
  assert.deepEqual(found('the fullness (v. 20) in vv. 3-5'), [
    ['v. 20', 'rel 20-20'],
    ['vv. 3-5', 'rel 3-5'],
  ]);
  const ref = findRefs('vv. 3-5')[0].ref;
  assert.equal(formatRef(resolveRelative(ref, parseRef('Romans 1:18'))), 'Romans 1:3–5');
  assert.equal(resolveRelative(ref, null), null);
});

test('parseRef reads frontmatter and data-ref values', () => {
  assert.deepEqual(parseRef('Ruth 3:9-13'), { book: 'Ruth', c1: 3, v1: 9, c2: 3, v2: 13 });
  assert.equal(parseRef('not a reference'), null);
});

test("Strong's tags inside the lexicons' range", () => {
  assert.deepEqual(findStrongs('(*aidios*, G126) and H0539a, not G9999 or AG12'), [
    { start: 11, end: 15, id: 'G126' },
    { start: 21, end: 27, id: 'H539' },
  ]);
});
