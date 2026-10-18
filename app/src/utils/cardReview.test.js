import test from 'node:test';
import assert from 'node:assert/strict';
import { INTERVAL_DAYS, NEW_PER_DAY, review, sessionQueue, spokenText } from './cardReview.js';

const DAY = 24 * 60 * 60 * 1000;
const NOW = Date.UTC(2026, 9, 18);
const deck = ['eli', 'elohim', 'adonai', 'yhwh', 'ehyeh'];

test('a first session introduces new cards in deck order, a few at a time', () => {
  assert.deepEqual(sessionQueue(deck, {}, NOW), deck.slice(0, NEW_PER_DAY));
});

test('cards already introduced today count against the new-card allowance', () => {
  assert.deepEqual(sessionQueue(deck, {}, NOW, NEW_PER_DAY), []);
});

test('due cards come before new ones; cards not yet due wait', () => {
  const progress = { eli: { box: 1, due: NOW - 1 }, elohim: { box: 2, due: NOW + DAY } };
  assert.deepEqual(sessionQueue(deck, progress, NOW), ['eli', 'adonai', 'yhwh', 'ehyeh']);
});

test('a correct reading moves a card up a box, and a new card read correctly returns tomorrow', () => {
  const first = review(undefined, true, NOW);
  assert.deepEqual(first, { box: 1, due: NOW + INTERVAL_DAYS[1] * DAY });
  assert.deepEqual(review(first, true, NOW), { box: 2, due: NOW + INTERVAL_DAYS[2] * DAY });
});

test('the top box holds rather than overflowing', () => {
  const top = INTERVAL_DAYS.length - 1;
  assert.equal(review({ box: top, due: NOW }, true, NOW).box, top);
});

test('a miss sends the card back to box 0, due again now', () => {
  assert.deepEqual(review({ box: 4, due: NOW }, false, NOW), { box: 0, due: NOW });
});

test('the divine name is spoken as Adonai, in a phrase and alone', () => {
  assert.equal(spokenText('יְהוָה רֹפְאֶךָ'), 'אֲדֹנָי רֹפְאֶךָ');
  assert.equal(spokenText('יהוה'), 'אֲדֹנָי');
  assert.equal(spokenText('אֵל שַׁדַּי'), 'אֵל שַׁדַּי');
  assert.equal(spokenText('אֲדֹנָי יְהוִה'), 'אֲדֹנָי אֱלֹהִים');
});
