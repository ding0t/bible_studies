/**
 * Chronology utilities for the Millennial Week timeline.
 *
 * "Anno Mundi" (AM) years are years-since-creation -- numerically identical to this
 * repo's existing `zadok_year` convention (see calendarConvert.js), just renamed here
 * because more than one epoch now maps AM to a Gregorian year (see chronology.json's
 * `epochs`), whereas calendarConvert.js's ZADOK_TO_GREGORIAN_OFFSET is fixed at 3959.
 */
import chronology from '../../../docs/data/chronology.json' with { type: 'json' };
import mtVariant from '../../../docs/data/genealogy/generated/mt.json' with { type: 'json' };
import lxxVariant from '../../../docs/data/genealogy/generated/lxx.json' with { type: 'json' };
import spVariant from '../../../docs/data/genealogy/generated/sp.json' with { type: 'json' };
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
};

export const GENEALOGY_INDEX = genealogyIndex;

// The site's epoch. Every derived year below goes through it, so moving the epoch is one edit in
// chronology.json and nothing else.
const SITE_EPOCH = 'genealogy';
const AD33 = 33;

// Each record stores ONE date -- am (Anno Mundi) for anything Genesis dates, gregorian for anything
// dated from Solomon onward -- and the other is derived here. Storing both is what turned the
// 2026-10-01 epoch change into a 374-number rewrite.
function bothCalendars(am, gregorian) {
  if (typeof am === 'number') return { am, gregorian: amToGregorian(am, SITE_EPOCH) };
  if (typeof gregorian === 'number') return { am: gregorianToAm(gregorian, SITE_EPOCH), gregorian };
  return { am: null, gregorian: null };
}

let eventsCache = null;

/**
 * Every dated event on the site, from one place: the Genesis markers, the anchor table, the other
 * archaeological anchors, the prophecy milestones, the AD 33 sequence and the life events. Each is
 * stored once; `people` names everyone it involves. Undated events (Scripture gives no year) carry
 * am and gregorian of null.
 */
export function loadEvents() {
  if (eventsCache) return eventsCache;
  const out = [];
  const add = (source, e, dates, extra = {}) =>
    out.push({
      ...e,
      ...extra,
      source,
      id: e.id,
      label: e.label,
      people: e.people ?? [],
      refs: e.refs ?? e.scripture ?? null,
      ...dates,
    });
  for (const e of chronology.genesis_markers) add('genesis', e, bothCalendars(e.am_year));
  for (const e of chronology.anchor_table) add('anchor', e, bothCalendars(null, e.gregorian_year));
  for (const e of chronology.anchors) add('archaeology', e, bothCalendars(null, e.gregorian_year));
  for (const e of chronology.milestones) add('milestone', e, bothCalendars(e.am_year, e.gregorian_year));
  for (const e of chronology.passion_sequence.events) add('passion', e, bothCalendars(null, AD33), { hour: e.at });
  for (const e of chronology.life_events) add('life', e, e.undated ? bothCalendars() : bothCalendars(e.am, e.gregorian));
  eventsCache = out;
  return out;
}

/** Events involving one person, in order; undated ones first, in the order they were recorded. */
export function eventsForPerson(personId) {
  return loadEvents()
    .filter((e) => e.people.includes(personId))
    .sort((a, b) => (a.am ?? -Infinity) - (b.am ?? -Infinity) || (a.hour ?? 0) - (b.hour ?? 0));
}

let peopleCache = null;

/**
 * The full genealogy, Adam through Jesus, merged from the six era files, with both calendars filled
 * in from the one each record stores and `major_events` assembled from the shared event list.
 * People with no stored year (Adam to Terah) get theirs from the generated variant files instead;
 * see mergePeopleWithVariant.
 */
export function loadGenealogyPeople() {
  if (peopleCache) return peopleCache;
  peopleCache = [
    ...antediluvian.people,
    ...patriarchal.people,
    ...conquestJudges.people,
    ...dividedKingdom.people,
    ...exileReturn.people,
    ...secondTemple.people,
  ].map((p) => {
    const born = bothCalendars(p.zadok_year_born, p.gregorian_year_born);
    const died = bothCalendars(p.zadok_year_died, p.gregorian_year_died);
    const events = eventsForPerson(p.id);
    return {
      ...p,
      ...(born.am != null && {
        zadok_year_born: born.am,
        gregorian_year_born: born.gregorian,
      }),
      ...(died.am != null && {
        zadok_year_died: died.am,
        gregorian_year_died: died.gregorian,
      }),
      major_events: events.length
        ? events.map((e) => ({
            event: e.label,
            zadok_year: e.am,
            gregorian_year: e.gregorian,
            description: e.description ?? e.note ?? e.evidence ?? '',
            refs: e.refs,
            source: e.source,
            id: e.id,
          }))
        : undefined,
    };
  });
  return peopleCache;
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
