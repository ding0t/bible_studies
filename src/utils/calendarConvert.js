/**
 * Calendar conversion utilities
 * 
 * Essene calendar: Year 0 = Adam's creation (4004 BC in Gregorian calendar)
 * Based on traditional biblical chronology (Ussher's calculation)
 */

// Offset between Essene Year 0 and Gregorian Year 1 AD
// Adam created in 4004 BC = Year -4003 in astronomical numbering = Essene Year 0
export const ESSENE_TO_GREGORIAN_OFFSET = 4004;

/**
 * Convert Essene year to Gregorian year
 * @param {number} esseneYear - Year in Essene calendar
 * @returns {number} Year in Gregorian calendar
 */
export function esseneToGregorian(esseneYear) {
  if (typeof esseneYear !== 'number' || isNaN(esseneYear)) {
    return null;
  }
  return esseneYear - ESSENE_TO_GREGORIAN_OFFSET;
}

/**
 * Convert Gregorian year to Essene year
 * @param {number} gregorianYear - Year in Gregorian calendar
 * @returns {number} Year in Essene calendar
 */
export function gregorianToEssene(gregorianYear) {
  if (typeof gregorianYear !== 'number' || isNaN(gregorianYear)) {
    return null;
  }
  return gregorianYear + ESSENE_TO_GREGORIAN_OFFSET;
}

/**
 * Get both calendar representations of a year
 * @param {number} year - Year in either calendar system
 * @param {string} sourceCalendar - 'essene' or 'gregorian'
 * @returns {Object} Object with both gregorian_year and essene_year
 */
export function getYearInBothCalendars(year, sourceCalendar = 'gregorian') {
  if (typeof year !== 'number' || isNaN(year)) {
    return { gregorian_year: null, essene_year: null };
  }

  if (sourceCalendar === 'essene') {
    return {
      essene_year: year,
      gregorian_year: esseneToGregorian(year)
    };
  } else {
    return {
      gregorian_year: year,
      essene_year: gregorianToEssene(year)
    };
  }
}

/**
 * Format year with calendar label
 * @param {number} year - Year value
 * @param {string} calendar - 'essene' or 'gregorian'
 * @returns {string} Formatted year string
 */
export function formatYearWithCalendar(year, calendar = 'gregorian') {
  if (typeof year !== 'number' || isNaN(year)) {
    return 'Unknown';
  }

  if (calendar === 'essene') {
    return `${year} (Essene)`;
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
  esseneToGregorian(4004) = 0     // Adam's birth year in Gregorian terms
  esseneToGregorian(5984) = 1980  // Year 1980 AD
  esseneToGregorian(6024) = 2020  // Year 2020 AD
  
  gregorianToEssene(1) = 4005     // 1 AD in Essene calendar
  gregorianToEssene(1948) = 5952  // 1948 AD (Israel founded)
  gregorianToEssene(2024) = 6028  // 2024 AD (current year)
  
  getYearInBothCalendars(2024) = { gregorian_year: 2024, essene_year: 6028 }
  getYearInBothCalendars(5984, 'essene') = { essene_year: 5984, gregorian_year: 1980 }
*/
