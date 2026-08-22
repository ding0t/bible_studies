/**
 * Calendar conversion utilities
 *
 * Zadok year = ELAPSED YEARS SINCE CREATION. Adam's creation is Zadok year 0, and the
 * creation year itself is 4004 BC on this site's working epoch (see
 * docs/content/feasts/zadok-calendar.md, "Where year 0 sits", for the epoch and the two
 * live alternatives).
 *
 * Gregorian years are signed with NO YEAR ZERO, matching how historians write BC/AD:
 *   negative => that many BC   (-4004 is 4004 BC)
 *   positive => that many AD   (1 is AD 1)
 *   zero     => invalid, and rejected
 *
 * The absence of a year zero is why this is not a plain subtraction. Before 2026-08-22 it
 * was, which put every AD conversion one year out: Zadok 4004 rendered as year 0 rather
 * than AD 1, and AD 2026 rendered as Zadok 6030 rather than 6029. The genealogy data
 * (docs/data/genealogy/generated/, Adam at zadok_year_born 0) and
 * docs/content/last-things/chronology-anchors.md both already used the corrected
 * convention, so this brings the converter into line with them rather than the reverse.
 */

// Zadok year of AD 1. Creation (Zadok 0) is 4004 BC, and the years 4004 BC through 1 BC are
// 4004 distinct years, so 4004 years elapse before AD 1 begins.
//
// Note the encoding is NEGATED-BC, not astronomical: -4004 here means 4004 BC. Astronomical
// (ISO 8601) numbering would make -4004 mean 4005 BC, because it has a year 0 equal to 1 BC.
// Do not feed these values to a date library that assumes ISO.
export const ZADOK_TO_GREGORIAN_OFFSET = 4004;

/**
 * Convert Zadok year to Gregorian year.
 * @param {number} zadokYear - Years elapsed since creation
 * @returns {number|null} Gregorian year, negative for BC, with no year zero
 */
export function zadokToGregorian(zadokYear) {
  if (typeof zadokYear !== 'number' || isNaN(zadokYear)) {
    return null;
  }
  const raw = zadokYear - ZADOK_TO_GREGORIAN_OFFSET;
  return raw < 0 ? raw : raw + 1;
}

/**
 * Convert Gregorian year to Zadok year.
 * @param {number} gregorianYear - Negative for BC, positive for AD; zero is invalid
 * @returns {number|null} Years elapsed since creation
 */
export function gregorianToZadok(gregorianYear) {
  if (typeof gregorianYear !== 'number' || isNaN(gregorianYear) || gregorianYear === 0) {
    return null;
  }
  return gregorianYear < 0
    ? gregorianYear + ZADOK_TO_GREGORIAN_OFFSET
    : gregorianYear - 1 + ZADOK_TO_GREGORIAN_OFFSET;
}

/**
 * Get both calendar representations of a year
 * @param {number} year - Year in either calendar system
 * @param {string} sourceCalendar - 'zadok' or 'gregorian'
 * @returns {Object} Object with both gregorian_year and zadok_year
 */
export function getYearInBothCalendars(year, sourceCalendar = 'gregorian') {
  if (typeof year !== 'number' || isNaN(year)) {
    return { gregorian_year: null, zadok_year: null };
  }

  if (sourceCalendar === 'zadok') {
    return {
      zadok_year: year,
      gregorian_year: zadokToGregorian(year)
    };
  } else {
    return {
      gregorian_year: year,
      zadok_year: gregorianToZadok(year)
    };
  }
}

/**
 * Format year with calendar label
 * @param {number} year - Year value
 * @param {string} calendar - 'zadok' or 'gregorian'
 * @returns {string} Formatted year string
 */
export function formatYearWithCalendar(year, calendar = 'gregorian') {
  if (typeof year !== 'number' || isNaN(year)) {
    return 'Unknown';
  }

  if (calendar === 'zadok') {
    return `${year} (Zadok)`;
  } else if (year === 0) {
    return 'Unknown'; // there is no year zero in BC/AD reckoning
  } else if (year < 0) {
    return `${Math.abs(year)} BC`;
  } else {
    return `${year} AD`;
  }
}

/**
 * Calculate year difference between two years (in either calendar)
 * @param {number} year1 - First year
 * @param {number} year2 - Second year
 * @returns {number} Absolute difference in years
 */
export function yearDifference(year1, year2) {
  if (typeof year1 !== 'number' || typeof year2 !== 'number' || isNaN(year1) || isNaN(year2)) {
    return null;
  }
  return Math.abs(year2 - year1);
}

// Example conversions:
/*
  zadokToGregorian(0)    = -4004  // creation, 4004 BC
  zadokToGregorian(1656) = -2348  // the Flood, 2348 BC
  zadokToGregorian(4003) = -1     // 1 BC
  zadokToGregorian(4004) = 1      // AD 1 -- there is no year zero to pass through
  zadokToGregorian(4036) = 33     // AD 33, the crucifixion
  zadokToGregorian(6029) = 2026   // AD 2026

  gregorianToZadok(-4004) = 0
  gregorianToZadok(-1)    = 4003
  gregorianToZadok(1)     = 4004
  gregorianToZadok(1948)  = 5951  // Israel founded
  gregorianToZadok(2026)  = 6029
  gregorianToZadok(0)     = null  // no year zero exists
*/
