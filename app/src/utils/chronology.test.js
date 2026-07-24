/**
 * Test cases for chronology utilities
 * Run with: node src/utils/chronology.test.js
 */

import {
  CHRONOLOGY,
  amToGregorian,
  gregorianToAm,
  mergePeopleWithVariant,
  getMillennialDay,
  loadGenealogyPeople,
  GENEALOGY_INDEX,
} from './chronology.js';

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FAILED: ${message}`);
    process.exit(1);
  } else {
    console.log(`✅ PASSED: ${message}`);
  }
}

console.log('\n📅 Chronology Tests\n');

console.log('1. AM <-> Gregorian per epoch:');
assert(amToGregorian(0, 'genealogy') === -4004, 'genealogy epoch: AM 0 = 4004 BC');
assert(amToGregorian(6000, 'genealogy') === 1996, 'genealogy epoch: AM 6000 = 1996 AD');
assert(amToGregorian(6000, 'millennial_2075') === 2075, 'millennial_2075 epoch: AM 6000 = 2075 AD');
assert(gregorianToAm(2075, 'millennial_2075') === 6000, 'millennial_2075 epoch round-trips AM 6000');
assert(amToGregorian(0, 'not_a_real_epoch') === null, 'unknown epoch returns null');
assert(amToGregorian(NaN, 'genealogy') === null, 'NaN AM year returns null');

console.log('\n2. Variant merge (Flood-relevant patriarchs diverge by tradition):');
const people = [
  { id: 'methuselah', gregorian_year_born: null, gregorian_year_died: null },
  { id: 'terah', gregorian_year_born: null, gregorian_year_died: null },
  { id: 'abraham', gregorian_year_born: -2166, gregorian_year_died: -1991 },
];

const mt = mergePeopleWithVariant(people, 'mt');
const sp = mergePeopleWithVariant(people, 'sp');
const harmonized = mergePeopleWithVariant(people, 'harmonized_v1');

const mtMethuselah = mt.find((p) => p.id === 'methuselah');
const spMethuselah = sp.find((p) => p.id === 'methuselah');
assert(mtMethuselah.lifespan_years === 969, 'MT Methuselah lifespan is 969 years');
assert(spMethuselah.lifespan_years === 720, 'SP Methuselah lifespan is 720 years (survives to the Flood)');

const mtTerah = mt.find((p) => p.id === 'terah');
const spTerah = sp.find((p) => p.id === 'terah');
assert(mtTerah.lifespan_years === 205, 'MT Terah lifespan is 205 years');
assert(spTerah.lifespan_years === 145, 'SP Terah lifespan is 145 years');

const harmonizedMethuselah = harmonized.find((p) => p.id === 'methuselah');
const harmonizedTerah = harmonized.find((p) => p.id === 'terah');
assert(harmonizedMethuselah.tradition_used === 'sp', 'harmonized_v1 adopts SP for Methuselah');
assert(harmonizedTerah.tradition_used === 'sp', 'harmonized_v1 adopts SP for Terah');

const mtAbraham = mt.find((p) => p.id === 'abraham');
assert(
  mtAbraham.gregorian_year_born === -2166,
  'people absent from a variant file (Abraham onward) pass through unchanged'
);

console.log('\n3. Millennial day lookup:');
const day1 = getMillennialDay(500);
assert(day1?.day === 1, 'AM 500 falls in Day 1');
const day7 = getMillennialDay(6500);
assert(day7?.day === 7 && day7.is_millennial_reign === true, 'AM 6500 falls in Day 7, the millennial reign');
assert(getMillennialDay(7000) === null, 'AM 7000 is past the last day band (end-exclusive)');

console.log('\n4. Chronology data sanity:');
assert(CHRONOLOGY.epochs.length === 2, 'exactly two epochs are defined');
assert(CHRONOLOGY.millennial_days.length === 7, 'exactly seven millennial days are defined');
assert(CHRONOLOGY.anchors.length > 0, 'at least one archaeological anchor is defined');

console.log('\n5. Genealogy loader:');
const genealogy = loadGenealogyPeople();
assert(genealogy.length === 77, 'loadGenealogyPeople merges all six era files (77 people)');
assert(genealogy.some((p) => p.id === 'adam'), 'Adam is present');
assert(genealogy.some((p) => p.id === 'jesus' || p.id === 'jesus_christ'), 'Jesus is present');
assert(Object.keys(GENEALOGY_INDEX.timeline_variants).length === 4, 'four timeline variants are indexed');

console.log('\n✨ All tests passed!\n');
