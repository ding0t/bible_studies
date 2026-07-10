import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { generateEvents } from './build-events.js';

const fixtureDir = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '__fixtures__/content'
);

test('includes only files with a year field', () => {
  const events = generateEvents(fixtureDir, '/bible_end_times');
  assert.equal(events.length, 1);
  assert.equal(events[0].title, 'Dated Study');
});

test('maps frontmatter and derives category, slug, url', () => {
  const [e] = generateEvents(fixtureDir, '/bible_end_times');
  assert.equal(e.slug, 'studies/prophecy/dated');
  assert.equal(e.category, 'prophecy');
  assert.equal(e.zadok_year, 3988);
  assert.equal(e.gregorian_year, 32);
  assert.deepEqual(e.tags, ['a', 'b']);
  assert.equal(e.url, '/bible_end_times/studies/prophecy/dated/');
});
