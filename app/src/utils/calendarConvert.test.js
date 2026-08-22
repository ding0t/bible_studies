/**
 * Test cases for calendar conversion functions
 * Run with: node src/utils/calendarConvert.test.js
 */

import {
  zadokToGregorian,
  gregorianToZadok,
  getYearInBothCalendars,
  formatYearWithCalendar,
  yearDifference,
  ZADOK_TO_GREGORIAN_OFFSET
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
assert(ZADOK_TO_GREGORIAN_OFFSET === 4004, 'Offset should be 4004');

// Test 2: Zadok to Gregorian conversions
// Zadok 0 is creation (4004 BC) and Zadok is an ELAPSED-YEAR count, so crossing from BC to
// AD skips the non-existent year zero. Zadok 4004 is AD 1, not year 0.
console.log('\n2. Zadok to Gregorian:');
assert(zadokToGregorian(0) === -4004, 'Zadok 0 = 4004 BC (creation)');
assert(zadokToGregorian(1656) === -2348, 'Zadok 1656 = 2348 BC (the Flood)');
assert(zadokToGregorian(4003) === -1, 'Zadok 4003 = 1 BC');
assert(zadokToGregorian(4004) === 1, 'Zadok 4004 = AD 1 (no year zero to pass through)');
assert(zadokToGregorian(4036) === 33, 'Zadok 4036 = AD 33 (the crucifixion)');
assert(zadokToGregorian(6029) === 2026, 'Zadok 6029 = AD 2026');

// Test 3: Gregorian to Zadok conversions
console.log('\n3. Gregorian to Zadok:');
assert(gregorianToZadok(-4004) === 0, '4004 BC = Zadok 0 (creation)');
assert(gregorianToZadok(-1) === 4003, '1 BC = Zadok 4003');
assert(gregorianToZadok(1) === 4004, 'AD 1 = Zadok 4004');
assert(gregorianToZadok(1948) === 5951, 'AD 1948 = Zadok 5951 (Israel founded)');
assert(gregorianToZadok(2026) === 6029, 'AD 2026 = Zadok 6029');
assert(gregorianToZadok(0) === null, 'Year zero does not exist and is rejected');

// Test 4: Round-trip conversions
console.log('\n4. Round-trip Conversions:');
for (let year of [1, 1948, 2026, -4004, -1, 500]) {
  const zadok = gregorianToZadok(year);
  const gregorian = zadokToGregorian(zadok);
  assert(gregorian === year, `Round-trip: Gregorian ${year} → Zadok ${zadok} → Gregorian ${gregorian}`);
}

// Test 5: getYearInBothCalendars
console.log('\n5. Get Year in Both Calendars:');
const both1 = getYearInBothCalendars(2026);
assert(both1.gregorian_year === 2026 && both1.zadok_year === 6029, 
  'Gregorian 2026 converts to both calendars correctly');

const both2 = getYearInBothCalendars(4036, 'zadok');
assert(both2.zadok_year === 4036 && both2.gregorian_year === 33,
  'Zadok 4036 converts to both calendars correctly');

// Test 6: Format year with calendar
console.log('\n6. Format Year with Calendar:');
assert(formatYearWithCalendar(2024, 'gregorian') === '2024 AD', 'Format Gregorian positive year');
assert(formatYearWithCalendar(-4003, 'gregorian') === '4003 BC', 'Format Gregorian negative year');
assert(formatYearWithCalendar(6028, 'zadok') === '6028 (Zadok)', 'Format Zadok year');

// Test 7: Year difference
console.log('\n7. Year Difference:');
assert(yearDifference(2024, 2020) === 4, 'Difference between 2024 and 2020 is 4 years');
assert(yearDifference(6028, 6024) === 4, 'Difference between Zadok years is 4 years');
assert(yearDifference(1948, 2024) === 76, 'Difference between 1948 and 2024 is 76 years');

// Test 8: Edge cases
console.log('\n8. Edge Cases:');
assert(zadokToGregorian(null) === null, 'Null input returns null');
assert(zadokToGregorian(undefined) === null, 'Undefined input returns null');
assert(zadokToGregorian(NaN) === null, 'NaN input returns null');
assert(getYearInBothCalendars(null).gregorian_year === null, 'Invalid year returns null values');

console.log('\n✨ All tests passed!\n');
