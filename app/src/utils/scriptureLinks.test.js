/**
 * Tests for the Scripture Links logic against the real exported data. Run with:
 * node --test src/utils/scriptureLinks.test.js
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../../../docs/data/scripture-links.json' with { type: 'json' };
import {
  METHODS,
  SCOPES,
  bookDegrees,
  bookFlows,
  entriesFor,
  indexByRef,
  inScope,
  lookupKey,
  matrix,
  methodBreakdown,
  topTargets,
} from './scriptureLinks.js';
import { linkIndex } from '../../scripts/build-links-index.js';

test('every method in the data has a label, colour and dash, or it would vanish from the diagrams', () => {
  for (const m of new Set(data.links.map((l) => l.m))) {
    assert.ok(METHODS[m], `method ${m} is in scripture-links.json but not in METHODS`);
    assert.ok(METHODS[m].color && METHODS[m].label);
  }
  for (const m of data.methodOrder) assert.ok(METHODS[m], `methodOrder names ${m}`);
});

test('a reader can type a book in full, abbreviated or with a dot', () => {
  assert.equal(lookupKey('Hebrews 10:5').key, 'Heb 10:5');
  assert.equal(lookupKey('heb 10.5').key, 'Heb 10:5');
  assert.equal(lookupKey('1 Corinthians 1:19').key, '1Cor 1:19');
  assert.equal(lookupKey('Isaiah 53').chapter, 'Isa 53');
  assert.equal(lookupKey('nonsense'), null);
});

test('a chapter lookup finds the links anywhere in it, and a verse lookup finds the verse', () => {
  const byRef = indexByRef(data.links);
  const verse = entriesFor(byRef, lookupKey('Heb 10:5'));
  assert.ok(verse.length > 0, 'Hebrews 10:5 has links');
  const chapter = entriesFor(byRef, lookupKey('Heb 10'));
  assert.ok(chapter.length >= verse.length);
  assert.ok(chapter.every((e) => e.at.startsWith('Heb 10:')));
});

test('the scopes partition the links: the three directions add up to all of them', () => {
  const count = (id) => data.links.filter((l) => inScope(l, id)).length;
  assert.equal(count('all'), data.links.length);
  assert.ok(count('nt-ot') > 0 && count('ot-ot') > 0);
  assert.equal(count('nt-ot') + count('ot-ot') + data.links.filter((l) => !inScope(l, 'nt-ot') && !inScope(l, 'ot-ot')).length, data.links.length);
  assert.deepEqual(SCOPES.map((s) => s.id), ['nt-ot', 'ot-ot', 'all']);
});

test('every diagram counts the same links the lookup holds', () => {
  const links = data.links;
  assert.equal(bookFlows(links).reduce((n, f) => n + f.links.length, 0), links.length);
  const { cells } = matrix(links);
  assert.equal([...cells.values()].reduce((n, c) => n + c.length, 0), links.length);
  assert.equal(bookDegrees(links).reduce((n, b) => n + b.n, 0), links.length * 2);
  const bars = methodBreakdown(links, data.methodOrder);
  assert.equal(bars.reduce((n, b) => n + b.total, 0), links.length);
  assert.ok(bars.every((b) => b.listed + b.found === b.total));
});

test('the most-quoted verses come back in descending order', () => {
  const top = topTargets(data.links.filter((l) => inScope(l, 'nt-ot')), 8);
  for (let i = 1; i < top.length; i++) assert.ok(top[i - 1].total >= top[i].total);
});

test('the pop-up index lists exactly the verses the lookup can answer for', () => {
  const index = linkIndex(data.links);
  const byRef = indexByRef(data.links);
  assert.deepEqual(Object.keys(index).sort(), [...byRef.keys()].sort());
  assert.equal(Object.values(index).reduce((n, [out]) => n + out, 0), data.links.length);
});
