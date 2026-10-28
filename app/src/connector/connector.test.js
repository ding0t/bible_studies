// The connector against a built site: run after `mkdocs build`, with CONNECTOR_SITE naming the
// site directory (the deploy workflow's "Test connector" step). It reads the same files the Worker
// reads through its ASSETS binding, so a missing export or a renamed field fails here, not live.

import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { test } from 'node:test';

import { createData } from './data.js';
import { handleMessage, TOOLS } from './server.js';

const SITE = process.env.CONNECTOR_SITE ?? join(import.meta.dirname, '../../../site');
const data = createData((path) => readFile(join(SITE, path), 'utf8').catch(() => null));

async function call(name, args = {}) {
  const response = await handleMessage(data, {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: { name, arguments: args },
  });
  assert.ok(response.result, JSON.stringify(response.error));
  const text = response.result.content[0].text;
  assert.ok(!response.result.isError, text);
  return JSON.parse(text);
}

test('initialize leads with the gospel', async () => {
  const { result } = await handleMessage(data, {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: { protocolVersion: '2025-06-18' },
  });
  assert.equal(result.protocolVersion, '2025-06-18');
  assert.match(result.instructions, /^The gospel:/);
  assert.equal(TOOLS[0].name, 'the_gospel');
});

test('the gospel quotes every verse it cites', async () => {
  const gospel = await call('the_gospel');
  assert.match(gospel.the_gospel, /Romans 3:23/);
  assert.ok(gospel.the_verses_it_rests_on.length >= 4);
  for (const v of gospel.the_verses_it_rests_on) assert.ok(v.text && v.translation, v.reference);
});

test("a question in a reader's words finds the study that answers it", async () => {
  const { results } = await call('search_studies', { query: 'How can I be sure I am saved?' });
  assert.equal(results[0].title, 'Assurance of Salvation');
});

test('a word only in the body of a study finds it, and the section', async () => {
  const { results } = await call('search_studies', { query: 'Tartarus' });
  assert.equal(results[0].title, 'At Home with the Lord');
  assert.match(results[0].best_sections[0].section, /Tartarus/);
  assert.match(results[0].best_sections[0].url, /#/);
});

test('a word the site never uses is reported, not stretched to fit', async () => {
  const result = await call('search_studies', { query: 'what does the bible say about tattoos' });
  assert.deepEqual(result.words_not_on_the_site, ['tattoos']);
});

test('beneath the English of John 21:15 is agapao', async () => {
  const { verses } = await call('beneath_the_english', { reference: 'john 21:15' });
  const love = verses[0].words.find((w) => /love/.test(w.english));
  assert.equal(love.strongs, 'G25');
});

test('John 21:15-17 shows two Greek words behind "love"', async () => {
  const result = await call('hidden_distinctions', { reference: 'John 21:15-17' });
  const love = result.one_english_word_for_several_original_words.find((d) => d.english === 'love');
  const ids = love.original_words.map((w) => w.strongs).sort();
  assert.deepEqual(ids, ['G25', 'G5368']);
});

test('a word study counts and lists occurrences', async () => {
  const word = await call('word_study', { strongs: 'G2894' });
  assert.equal(word.lemma.normalize('NFC'), 'κόφινος'.normalize('NFC'));
  assert.ok(word.verses_in_the_hebrew_or_greek_text >= 6);
});

test('Hebrews 10:5 traces to Psalm 40', async () => {
  const { verses } = await call('quotation_trace', { reference: 'Hebrews 10:5' });
  assert.ok(verses[0].links.some((l) => /Psalms? 40:6/.test(l.english_reference ?? '')));
});

test('English Joel 2:28 is Hebrew Joel 3:1', async () => {
  const { verses } = await call('read_passage', { reference: 'Joel 2:28' });
  assert.equal(verses[0].numbered_elsewhere_as.masoretic, 'Joel 3:1');
});

test('a person carries both calendars and contemporaries', async () => {
  const shem = await call('person', { name: 'Shem' });
  assert.ok(shem.alive_at_the_same_time.some((p) => p.name === 'Abraham'));
});

test('years convert both ways on the site epoch', async () => {
  assert.equal((await call('convert_year', { year: 'AD 1' })).am, 3959);
  assert.equal((await call('convert_year', { year: 'AM 2513' })).year, '1446 BC');
});

test('a traditional grammar name finds the article under its tag name', async () => {
  const waw = await call('hebrew_grammar', { topic: 'waw consecutive' });
  assert.equal(waw.article.title, 'Verb Sequential Imperfect');
  assert.equal(
    (await call('hebrew_grammar', { topic: 'weqatal' })).article.title,
    'Verb Sequential Perfect'
  );
});

test('a skill is served as a prompt with the connector adapter', async () => {
  const { result } = await handleMessage(data, {
    jsonrpc: '2.0',
    id: 1,
    method: 'prompts/get',
    params: { name: 'develop_bible_study', arguments: { passage_or_topic: 'Ezekiel 9' } },
  });
  const text = result.messages[0].content.text;
  assert.match(text, /beneath_the_english/);
  assert.match(text, /# Develop a Bible Study/);
});

test('a bad reference is a tool error, not a protocol error', async () => {
  const response = await handleMessage(data, {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: { name: 'read_passage', arguments: { reference: 'Hezekiah 4:1' } },
  });
  assert.equal(response.result.isError, true);
});
