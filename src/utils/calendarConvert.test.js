/**
 * Test cases for calendar conversion functions
 * Run with: node src/utils/calendarConvert.test.js
 */

import {
  esseneToGregorian,
  gregorianToEssene,
  getYearInBothCalendars,
  formatYearWithCalendar,
  yearDifference,
  ESSENE_TO_GREGORIAN_OFFSET
} from './calendarConvert.js';

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FAILED: ${message}`);
    process.exit(1);
  } else {
    console.log(`✅ PASSED: ${message}`);
  }
}

console.log('\n📅 Calendar Conversion Tests\n');

// Test 1: Offset constant
console.log('1. Offset Constant:');
assert(ESSENE_TO_GREGORIAN_OFFSET === 4004, 'Offset should be 4004');

// Test 2: Essene to Gregorian conversions
console.log('\n2. Essene to Gregorian:');
assert(esseneToGregorian(4004) === 0, 'Essene 4004 = Gregorian 0 (Adam\'s year)');
assert(esseneToGregorian(5984) === 1980, 'Essene 5984 = Gregorian 1980');
assert(esseneToGregorian(6028) === 2024, 'Essene 6028 = Gregorian 2024');
assert(esseneToGregorian(4005) === 1, 'Essene 4005 = Gregorian 1 (1 AD)');

// Test 3: Gregorian to Essene conversions
console.log('\n3. Gregorian to Essene:');
assert(gregorianToEssene(1) === 4005, 'Gregorian 1 = Essene 4005 (1 AD)');
assert(gregorianToEssene(1948) === 5952, 'Gregorian 1948 = Essene 5952 (Israel founded)');
assert(gregorianToEssene(2024) === 6028, 'Gregorian 2024 = Essene 6028');
assert(gregorianToEssene(-4003) === 1, 'Gregorian -4003 = Essene 1 (4004 BC)');

// Test 4: Round-trip conversions
console.log('\n4. Round-trip Conversions:');
for (let year of [1, 1948, 2024, -4003, 500]) {
  const essene = gregorianToEssene(year);
  const gregorian = esseneToGregorian(essene);
  assert(gregorian === year, `Round-trip: Gregorian ${year} → Essene ${essene} → Gregorian ${gregorian}`);
}

// Test 5: getYearInBothCalendars
console.log('\n5. Get Year in Both Calendars:');
const both1 = getYearInBothCalendars(2024);
assert(both1.gregorian_year === 2024 && both1.essene_year === 6028, 
  'Gregorian 2024 converts to both calendars correctly');

const both2 = getYearInBothCalendars(5984, 'essene');
assert(both2.essene_year === 5984 && both2.gregorian_year === 1980,
  'Essene 5984 converts to both calendars correctly');

// Test 6: Format year with calendar
console.log('\n6. Format Year with Calendar:');
assert(formatYearWithCalendar(2024, 'gregorian') === '2024 AD', 'Format Gregorian positive year');
assert(formatYearWithCalendar(-4003, 'gregorian') === '4003 BC', 'Format Gregorian negative year');
assert(formatYearWithCalendar(6028, 'essene') === '6028 (Essene)', 'Format Essene year');

// Test 7: Year difference
console.log('\n7. Year Difference:');
assert(yearDifference(2024, 2020) === 4, 'Difference between 2024 and 2020 is 4 years');
assert(yearDifference(6028, 6024) === 4, 'Difference between Essene years is 4 years');
assert(yearDifference(1948, 2024) === 76, 'Difference between 1948 and 2024 is 76 years');

// Test 8: Edge cases
console.log('\n8. Edge Cases:');
assert(esseneToGregorian(null) === null, 'Null input returns null');
assert(esseneToGregorian(undefined) === null, 'Undefined input returns null');
assert(esseneToGregorian(NaN) === null, 'NaN input returns null');
assert(getYearInBothCalendars(null).gregorian_year === null, 'Invalid year returns null values');

console.log('\n✨ All tests passed!\n');
