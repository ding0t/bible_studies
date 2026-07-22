/**
 * Calendar conversion utilities
 * 
 * Zadok calendar: Year 0 = Adam's creation (4004 BC in Gregorian calendar)
 * Based on traditional biblical chronology (Ussher's calculation)
 */

// Offset between Zadok Year 0 and Gregorian Year 1 AD
// Adam created in 4004 BC = Year -4003 in astronomical numbering = Zadok Year 0
export const ZADOK_TO_GREGORIAN_OFFSET = 4004;

/**
 * Convert Zadok year to Gregorian year
 * @param {number} zadokYear - Year in Zadok calendar
 * @returns {number} Year in Gregorian calendar
 */
export function zadokToGregorian(zadokYear) {
  if (typeof zadokYear !== 'number' || isNaN(zadokYear)) {
    return null;
  }
  return zadokYear - ZADOK_TO_GREGORIAN_OFFSET;
}

/**
 * Convert Gregorian year to Zadok year
 * @param {number} gregorianYear - Year in Gregorian calendar
 * @returns {number} Year in Zadok calendar
 */
export function gregorianToZadok(gregorianYear) {
  if (typeof gregorianYear !== 'number' || isNaN(gregorianYear)) {
    return null;
  }
  return gregorianYear + ZADOK_TO_GREGORIAN_OFFSET;
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
  } else if (year < 1) {
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

// Example conversions for documentation:
/*
  zadokToGregorian(4004) = 0     // Adam's birth year in Gregorian terms
  zadokToGregorian(5984) = 1980  // Year 1980 AD
  zadokToGregorian(6024) = 2020  // Year 2020 AD
  
  gregorianToZadok(1) = 4005     // 1 AD in Zadok calendar
  gregorianToZadok(1948) = 5952  // 1948 AD (Israel founded)
  gregorianToZadok(2024) = 6028  // 2024 AD (current year)

  getYearInBothCalendars(2024) = { gregorian_year: 2024, zadok_year: 6028 }
  getYearInBothCalendars(5984, 'zadok') = { zadok_year: 5984, gregorian_year: 1980 }
*/
