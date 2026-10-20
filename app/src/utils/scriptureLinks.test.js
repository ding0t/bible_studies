/**
 * Tests for the Scripture Links logic against the real exported data. Run with:
 * node --test src/utils/scriptureLinks.test.js
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../../../docs/data/scripture-links.json' with { type: 'json' };
import method from '../../../docs/data/link-method.json' with { type: 'json' };
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
  basisWords,
  RULES,
  calibration,
  confirmationFor,
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

test('every rule that admitted a link has plain words for the "found by" line', () => {
  for (const basis of new Set(data.links.map((l) => l.b))) {
    assert.ok(basis, 'a link with no basis');
    assert.equal(basisWords(basis).length, basis.split('+').length - (basis.includes('formula+phrases') ? 1 : 0), basis);
  }
});

test('every rule the build reports has a profile, and every profile a rule, or a card would be blank', () => {
  const profiled = new Set(RULES.map((r) => r.id));
  for (const id of Object.keys(method.rules)) assert.ok(profiled.has(id), `rule ${id} has no profile in RULES`);
  for (const id of profiled) assert.ok(method.rules[id], `RULES profiles ${id}, which the build no longer reports`);
});

test('each answer key is accounted for: found by some rules or listed as missed', () => {
  for (const key of [method.key, method.otKey]) {
    assert.equal(key.foundBy.reduce((s, f) => s + f.n, 0), key.total);
    assert.equal(key.foundBy.find((f) => f.rules.length === 0)?.n ?? 0, key.missed.length);
  }
});

test('a link\'s trust line is the confirmed share of links found the same way', () => {
  const cal = calibration(data.links);
  const link = data.links.find((l) => l.f === 'John 10:34');
  const same = data.links.filter((l) => l.m === link.m && l.b === link.b);
  const t = confirmationFor(cal, link);
  assert.ok(t.exact && same.length >= 10);
  assert.equal(t.c, same.filter((l) => l.c).length);
  assert.equal(t.n, same.length);
});
