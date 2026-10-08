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
  loadEvents,
  eventsForPerson,
  GENEALOGY_INDEX,
  VARIANTS,
} from './chronology.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const CONTENT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../docs/content');

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
assert(amToGregorian(0, 'genealogy') === -3959, 'genealogy epoch: AM 0 = 3959 BC');
assert(amToGregorian(6000, 'genealogy') === 2042, 'genealogy epoch: AM 6000 = AD 2042');
assert(amToGregorian(3959, 'genealogy') === 1, 'genealogy epoch: AM 3959 = AD 1, not year 0');
assert(amToGregorian(3958, 'genealogy') === -1, 'genealogy epoch: AM 3958 = 1 BC');
assert(gregorianToAm(0, 'genealogy') === null, 'year zero does not exist');
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

const mtMethuselah = mt.find((p) => p.id === 'methuselah');
const spMethuselah = sp.find((p) => p.id === 'methuselah');
assert(mtMethuselah.lifespan_years === 969, 'MT Methuselah lifespan is 969 years');
assert(spMethuselah.lifespan_years === 720, 'SP Methuselah lifespan is 720 years (dies in the Flood year)');

const mtTerah = mt.find((p) => p.id === 'terah');
const spTerah = sp.find((p) => p.id === 'terah');
assert(mtTerah.lifespan_years === 205, 'MT Terah lifespan is 205 years');
assert(spTerah.lifespan_years === 145, 'SP Terah lifespan is 145 years');

// The working chronology is MT throughout (2026-09-28): harmonized_v1, which took SP's Terah,
// was retired. SP keeps its own reading of Terah (70 at Abram's birth, 145 total), so its Terah
// dies in the year Abram leaves Haran at 75 (Genesis 12:4; Acts 7:4).
assert(mtTerah.tradition_used === 'mt' && mtMethuselah.tradition_used === 'mt', 'MT variant uses MT for Methuselah and Terah');
assert(VARIANTS.harmonized_v1 === undefined, 'the retired harmonized_v1 variant is no longer loaded');
assert(VARIANTS.sp.creation_bc === 4200, 'SP creation is 4200 BC once SP Terah is read on its own terms (Flood 2893 BC, Exodus 1446 BC)');

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
assert(genealogy.length === 78, 'loadGenealogyPeople merges all six era files (78 people)');
assert(genealogy.some((p) => p.id === 'adam'), 'Adam is present');
assert(genealogy.some((p) => p.id === 'jesus' || p.id === 'jesus_christ'), 'Jesus is present');
assert(Object.keys(GENEALOGY_INDEX.timeline_variants).length === 3, 'three timeline variants are indexed (mt, lxx, sp)');

console.log('\n6. Timeline agrees with Chronology Anchors:');
// The timeline's anchor rows are a copy of the table on chronology-anchors.md. A study edited
// without the data, or the data without the study, is exactly the drift this site keeps finding.
const anchorsMd = fs.readFileSync(path.join(CONTENT, 'chronology/chronology-anchors.md'), 'utf8');
const tableRows = anchorsMd
  .split('\n')
  .filter((l) => /^\| \d+ \|/.test(l))
  .map((l) =>
    l
      .split('|')
      .slice(1, -1)
      .map((c) => c.trim().replace(/\*/g, ''))
  );
const parseYear = (s) => {
  const m = s.match(/^(AD )?(\d+)( BC)?$/);
  return m[3] ? -Number(m[2]) : Number(m[2]);
};
assert(
  tableRows.length === CHRONOLOGY.anchor_table.length,
  `anchor_table has one entry per table row (${tableRows.length})`
);
for (const [n, , , date, tier, err, zadok] of tableRows) {
  const e = CHRONOLOGY.anchor_table.find((a) => a.n === Number(n));
  const same =
    e &&
    e.gregorian_year === parseYear(date) &&
    e.tier === tier &&
    e.error === err &&
    e.zadok_year === Number(zadok);
  assert(same, `row ${n} (${date}) matches the page`);
  assert(
    gregorianToAm(e.gregorian_year, 'genealogy') === e.zadok_year,
    `row ${n}'s Zadok year is its date on the site's epoch`
  );
}

console.log('\n7. Every timeline link opens a published study:');
const refs = new Set(
  [
    ...CHRONOLOGY.epochs,
    ...CHRONOLOGY.anchors,
    ...CHRONOLOGY.anchor_table,
    ...CHRONOLOGY.milestones,
    ...CHRONOLOGY.genesis_markers,
    ...CHRONOLOGY.future_sequence.events,
    ...CHRONOLOGY.passion_sequence.events,
  ]
    .map((x) => x.study_ref)
    .filter(Boolean)
);
for (const ref of refs) {
  const file = path.join(CONTENT, `${ref}.md`);
  const exists = fs.existsSync(file);
  assert(
    exists && !/^draft: true$/m.test(fs.readFileSync(file, 'utf8')),
    `${ref} exists and is published`
  );
}

console.log('\n8. The undated future sequence keeps its stated lengths:');
const fut = Object.fromEntries(CHRONOLOGY.future_sequence.events.map((e) => [e.id, e]));
assert(
  fut.covenant.at === 0 && fut.second_coming.at === 7,
  'the seventieth week runs seven years from the covenant (Daniel 9:27)'
);
assert(fut.abomination.at === 3.5, 'the abomination falls at its midpoint, day 1,260');
assert(
  Math.round((fut.days_1290.at - fut.abomination.at) * 360) === 1290,
  '1,290 days counted from the abomination (Daniel 12:11)'
);
assert(
  Math.round((fut.days_1335.at - fut.abomination.at) * 360) === 1335,
  '1,335 days counted from the abomination (Daniel 12:12)'
);
assert(
  fut.millennium.end - fut.millennium.at === 1000,
  'the millennium is a thousand years (Revelation 20)'
);
assert(
  CHRONOLOGY.future_sequence.events.every(
    (e) => e.gregorian_year === undefined && e.am_year === undefined
  ),
  'no future event carries a calendar date'
);

console.log('\n9. AD 33 passion sequence:');
const pdays = Object.fromEntries(CHRONOLOGY.passion_sequence.days.map((d) => [d.hebrew, d]));
assert(pdays['14 Nisan'].daylight === 'Friday 3 April', 'Nisan 14 is Friday 3 April, the crucifixion');
assert(pdays['15 Nisan'].sabbath && pdays['15 Nisan'].daylight === 'Saturday 4 April', 'Nisan 15, the first day of Unleavened Bread, is the Sabbath');
assert(pdays['16 Nisan'].daylight === 'Sunday 5 April', 'Firstfruits, Nisan 16, is Sunday 5 April');
assert(pdays['6 Sivan'].daylight === 'Sunday 24 May', 'Pentecost, the fiftieth day, is Sunday 24 May');
assert((pdays['6 Sivan'].start - pdays['16 Nisan'].start) / 24 === 49, 'Firstfruits to Pentecost is fifty days counted inclusively (Leviticus 23:15-16)');
const nights = CHRONOLOGY.passion_sequence.three_days.filter((b) => b.kind === 'night').length;
const dayCount = CHRONOLOGY.passion_sequence.three_days.filter((b) => b.kind === 'day').length;
assert(nights === 2 && dayCount === 3, 'three days touched and two nights, as Three Days and Three Nights counts them');

console.log('\n10. One set of facts:');
// Each fact is stored once. These checks are what keep a future epoch change a one-line edit.
const allEvents = loadEvents();
const personIds = new Set(loadGenealogyPeople().map((p) => p.id));
assert(
  allEvents.every((e) => e.people.every((id) => personIds.has(id))),
  'every person an event names exists in the genealogy'
);
assert(
  CHRONOLOGY.life_events.every((e) => !(('am' in e) && ('gregorian' in e))),
  'no life event stores both calendars'
);
assert(
  CHRONOLOGY.life_events.every((e) => e.undated || 'am' in e || 'gregorian' in e),
  'every life event is dated once, or marked undated'
);
const eventIds = allEvents.map((e) => `${e.source}:${e.id}`);
assert(new Set(eventIds).size === eventIds.length, 'no event id is used twice within a collection');
const perPersonDupes = [];
for (const id of personIds) {
  const seen = new Set();
  for (const e of eventsForPerson(id)) {
    const key = `${e.am}|${e.label.toLowerCase()}`;
    if (seen.has(key)) perPersonDupes.push(`${id}: ${e.label}`);
    seen.add(key);
  }
}
assert(perPersonDupes.length === 0, `no person has the same event twice (${perPersonDupes.join('; ')})`);
const allPeople = loadGenealogyPeople();
assert(
  allPeople.every((p) => p.zadok_year_born == null || gregorianToAm(p.gregorian_year_born, 'genealogy') === p.zadok_year_born),
  "each person's two calendars are derived from one, and agree"
);
assert(
  allPeople.every((p) => p.zadok_year_born == null || p.zadok_year_died == null || p.zadok_year_died - p.zadok_year_born === p.lifespan_years),
  'every lifespan equals death minus birth'
);
const jacob = allPeople.find((p) => p.id === 'jacob');
assert(jacob.zadok_year_died - jacob.zadok_year_born === 147, 'Jacob dies at 147 (Genesis 47:28)');
assert(jacob.zadok_year_died === 2298 + 17, 'Jacob dies seventeen years after entering Egypt (Genesis 47:28)');
const sarah = allPeople.find((p) => p.id === 'sarah');
assert(sarah.lifespan_years === 127 && sarah.zadok_year_born === 2008 + 10, 'Sarah is ten years younger than Abraham and dies at 127 (Genesis 17:17; 23:1)');
const abrahamEvents = eventsForPerson('abraham').map((e) => e.id);
assert(abrahamEvents.includes('abram_called') && abrahamEvents.includes('isaac_born'), "Abraham's call and Isaac's birth are the Genesis markers, not copies of them");
assert(eventsForPerson('jesus').some((e) => e.source === 'passion' && e.id === 'crucified'), "Jesus's crucifixion is the AD 33 sequence's event, not a copy");

console.log('\n✨ All tests passed!\n');
