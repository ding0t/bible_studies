import test from 'node:test';
import assert from 'node:assert/strict';
import { spokenText } from './speech.js';

test('the divine name is spoken as Adonai, in a phrase and alone', () => {
  assert.equal(spokenText('יְהוָה רֹפְאֶךָ'), 'אֲדֹנָי רֹפְאֶךָ');
  assert.equal(spokenText('יהוה'), 'אֲדֹנָי');
  assert.equal(spokenText('אֵל שַׁדַּי'), 'אֵל שַׁדַּי');
});

test('the lexicon pointing and a prefixed name are read Adonai, never sounded out', () => {
  assert.equal(spokenText('יְהֹוָה'), 'אֲדֹנָי');
  assert.equal(spokenText('לַיהוָה'), 'לַאֲדֹנָי');
  assert.equal(spokenText('יְהוָ֣ה'), 'אֲדֹנָי');
});

test('the name pointed for Elohim after Adonai is read Elohim', () => {
  assert.equal(spokenText('אֲדֹנָי יְהוִה'), 'אֲדֹנָי אֱלֹהִים');
  assert.equal(spokenText('יֱהֹוִה'), 'אֱלֹהִים');
});

test('names that share letters with the divine name are left alone', () => {
  assert.equal(spokenText('יְהוּדָה'), 'יְהוּדָה');
  assert.equal(spokenText('יְהוֹשֻׁעַ'), 'יְהוֹשֻׁעַ');
});

test('chanting marks go and maqaf becomes a space', () => {
  assert.equal(spokenText('בְּהִבָּֽרְאָם'), 'בְּהִבָּרְאָם');
  assert.equal(spokenText('כָּל־הָאָרֶץ'), 'כָּל הָאָרֶץ');
});

test('Greek is read monotonic: breathings and iota subscript go, every accent becomes acute', () => {
  assert.equal(spokenText('Ἐν ἀρχῇ ἦν ὁ Λόγος', 'el'), 'Εν αρχή ήν ο Λόγος');
});
