/**
 * Chronology utilities for the Millennial Week timeline.
 *
 * "Anno Mundi" (AM) years are years-since-creation -- numerically identical to this
 * repo's existing `zadok_year` convention (see calendarConvert.js), just renamed here
 * because more than one epoch now maps AM to a Gregorian year (see chronology.json's
 * `epochs`), whereas calendarConvert.js's ZADOK_TO_GREGORIAN_OFFSET is fixed at 4004.
 */
import chronology from '../../../docs/data/chronology.json' with { type: 'json' };
import mtVariant from '../../../docs/data/genealogy/generated/mt.json' with { type: 'json' };
import lxxVariant from '../../../docs/data/genealogy/generated/lxx.json' with { type: 'json' };
import spVariant from '../../../docs/data/genealogy/generated/sp.json' with { type: 'json' };
import harmonizedVariant from '../../../docs/data/genealogy/generated/harmonized_v1.json' with { type: 'json' };
import genealogyIndex from '../../../docs/data/genealogy/index.json' with { type: 'json' };
import antediluvian from '../../../docs/data/genealogy/antediluvian.json' with { type: 'json' };
import patriarchal from '../../../docs/data/genealogy/patriarchal.json' with { type: 'json' };
import conquestJudges from '../../../docs/data/genealogy/conquest-judges.json' with { type: 'json' };
import dividedKingdom from '../../../docs/data/genealogy/divided-kingdom.json' with { type: 'json' };
import exileReturn from '../../../docs/data/genealogy/exile-return.json' with { type: 'json' };
import secondTemple from '../../../docs/data/genealogy/second-temple.json' with { type: 'json' };

export const CHRONOLOGY = chronology;

export const VARIANTS = {
  mt: mtVariant,
  lxx: lxxVariant,
  sp: spVariant,
  harmonized_v1: harmonizedVariant,
};

export const GENEALOGY_INDEX = genealogyIndex;

/** The full 77-person genealogy, Adam through Jesus, merged from the six era files. */
export function loadGenealogyPeople() {
  return [
    ...antediluvian.people,
    ...patriarchal.people,
    ...conquestJudges.people,
    ...dividedKingdom.people,
    ...exileReturn.people,
    ...secondTemple.people,
  ];
}

export function getEpoch(epochId) {
  return chronology.epochs.find((e) => e.id === epochId) ?? null;
}

/**
 * AM to Gregorian, skipping the non-existent year zero.
 *
 * Gregorian years are signed with no year zero: negative is BC, positive is AD. So an AM
 * year that lands at or past the era boundary gains one. Same correction as
 * calendarConvert.js -- both were plain additions until 2026-08-22, which put every AD
 * result a year early.
 */
export function amToGregorian(amYear, epochId) {
  const epoch = getEpoch(epochId);
  if (!epoch || typeof amYear !== 'number' || isNaN(amYear)) return null;
  const raw = amYear + epoch.am0_gregorian;
  return raw < 0 ? raw : raw + 1;
}

export function gregorianToAm(gregorianYear, epochId) {
  const epoch = getEpoch(epochId);
  if (!epoch || typeof gregorianYear !== 'number' || isNaN(gregorianYear)) return null;
  if (gregorianYear === 0) return null; // no year zero exists
  const adjusted = gregorianYear < 0 ? gregorianYear : gregorianYear - 1;
  return adjusted - epoch.am0_gregorian;
}

/**
 * Returns a new people array with any person present in the variant's data
 * overriding that person's born/died years. Genesis gives age-at-heir-birth
 * data only through Terah, so only Adam-Terah are ever present in a variant
 * file; everyone else passes through unchanged.
 */
export function mergePeopleWithVariant(people, variantId) {
  const variant = VARIANTS[variantId];
  if (!variant) return people;
  return people.map((person) => {
    const override = variant.people[person.id];
    if (!override) return person;
    return {
      ...person,
      zadok_year_born: override.zadok_year_born,
      zadok_year_died: override.zadok_year_died,
      gregorian_year_born: override.gregorian_year_born,
      gregorian_year_died: override.gregorian_year_died,
      lifespan_years: override.lifespan_years,
      tradition_used: override.tradition_used,
    };
  });
}

export function getMillennialDay(amYear) {
  return chronology.millennial_days.find((d) => amYear >= d.am_start && amYear < d.am_end) ?? null;
}
