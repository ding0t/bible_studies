/**
 * Bible Reference Parser Tests
 * Run with: node src/utils/bibleReference.test.js
 */

import { parseReference, generateBibleLink, getSiteDisplayName } from './bibleReference.js';

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`✓ ${name}`);
  } catch (e) {
    failed++;
    console.log(`✗ ${name}`);
    console.log(`  Error: ${e.message}`);
  }
}

function assertEqual(actual, expected, message = '') {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${message}\n  Expected: ${JSON.stringify(expected)}\n  Actual: ${JSON.stringify(actual)}`);
  }
}

function assertNull(actual, message = '') {
  if (actual !== null) {
    throw new Error(`${message}\n  Expected: null\n  Actual: ${JSON.stringify(actual)}`);
  }
}

console.log('Bible Reference Parser Tests\n' + '='.repeat(40));

// parseReference tests
console.log('\n--- parseReference ---');

test('parses simple reference: Genesis 1:27', () => {
  const result = parseReference('Genesis 1:27');
  assertEqual(result.book, 'genesis');
  assertEqual(result.bookShort, 'gen');
  assertEqual(result.bookNum, 1);
  assertEqual(result.chapter, 1);
  assertEqual(result.verses, [27]);
  assertEqual(result.firstVerse, 27);
});

test('parses verse range: John 3:16-18', () => {
  const result = parseReference('John 3:16-18');
  assertEqual(result.book, 'john');
  assertEqual(result.bookShort, 'joh');
  assertEqual(result.chapter, 3);
  assertEqual(result.verses, [16, 17, 18]);
  assertEqual(result.firstVerse, 16);
});

test('parses numbered book: 1 Corinthians 13:4', () => {
  const result = parseReference('1 Corinthians 13:4');
  assertEqual(result.book, '1 corinthians');
  assertEqual(result.bookShort, '1co');
  assertEqual(result.bookNum, 46);
  assertEqual(result.chapter, 13);
  assertEqual(result.verses, [4]);
});

test('parses numbered book with range: 2 Timothy 3:16-17', () => {
  const result = parseReference('2 Timothy 3:16-17');
  assertEqual(result.book, '2 timothy');
  assertEqual(result.chapter, 3);
  assertEqual(result.verses, [16, 17]);
});

test('handles case insensitivity: GENESIS 1:1', () => {
  const result = parseReference('GENESIS 1:1');
  assertEqual(result.book, 'genesis');
  assertEqual(result.chapter, 1);
});

test('handles Psalm/Psalms variants', () => {
  const psalm = parseReference('Psalm 23:1');
  const psalms = parseReference('Psalms 23:1');
  assertEqual(psalm.bookNum, 19);
  assertEqual(psalms.bookNum, 19);
});

test('handles Song of Solomon variants', () => {
  const sos1 = parseReference('Song of Solomon 1:1');
  const sos2 = parseReference('Song of Songs 1:1');
  assertEqual(sos1.bookNum, 22);
  assertEqual(sos2.bookNum, 22);
});

test('returns null for invalid input: null', () => {
  assertNull(parseReference(null));
});

test('returns null for invalid input: empty string', () => {
  assertNull(parseReference(''));
});

test('returns null for invalid input: number', () => {
  assertNull(parseReference(123));
});

test('returns null for unknown book', () => {
  assertNull(parseReference('FakeBook 1:1'));
});

test('returns null for malformed reference', () => {
  assertNull(parseReference('Genesis'));
  assertNull(parseReference('Genesis 1'));
  assertNull(parseReference('1:27'));
});

// generateBibleLink tests
console.log('\n--- generateBibleLink ---');

test('generates Blue Letter Bible link', () => {
  const parsed = parseReference('Genesis 1:27');
  const link = generateBibleLink(parsed, 'esv', 'blueletterbible');
  assertEqual(link, 'https://www.blueletterbible.org/esv/genesis/1/27/');
});

test('generates Bible Gateway link', () => {
  const parsed = parseReference('John 3:16');
  const link = generateBibleLink(parsed, 'niv', 'biblegateway');
  assertEqual(link.includes('biblegateway.com'), true);
  assertEqual(link.includes('NIV'), true);
});

test('generates BibleHub link', () => {
  const parsed = parseReference('Romans 8:28');
  const link = generateBibleLink(parsed, 'esv', 'biblehub');
  assertEqual(link, 'https://biblehub.com/romans/8-28.htm');
});

test('defaults to Blue Letter Bible for unknown site', () => {
  const parsed = parseReference('Genesis 1:1');
  const link = generateBibleLink(parsed, 'esv', 'unknownsite');
  assertEqual(link.includes('blueletterbible.org'), true);
});

test('returns null for null parsed reference', () => {
  assertNull(generateBibleLink(null));
});

// getSiteDisplayName tests
console.log('\n--- getSiteDisplayName ---');

test('returns Blue Letter Bible display name', () => {
  assertEqual(getSiteDisplayName('blueletterbible'), 'Blue Letter Bible');
});

test('returns Bible Gateway display name', () => {
  assertEqual(getSiteDisplayName('biblegateway'), 'Bible Gateway');
});

test('returns BibleHub display name', () => {
  assertEqual(getSiteDisplayName('biblehub'), 'BibleHub');
});

test('returns original key for unknown site', () => {
  assertEqual(getSiteDisplayName('customsite'), 'customsite');
});

// Summary
console.log('\n' + '='.repeat(40));
console.log(`Results: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
