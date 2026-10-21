// The chronology and prophecy tools, over the same data the Prophetic Timeline draws:
// docs/data/chronology.json and the genealogy, through app/src/utils/chronology.js, so the
// connector and the timeline can never disagree about a date. Bundled at build, so every deploy
// serves the current chronology.

import {
  CHRONOLOGY,
  amToGregorian,
  getMillennialDay,
  gregorianToAm,
  loadEvents,
  loadGenealogyPeople,
  mergePeopleWithVariant,
} from '../utils/chronology.js';
import { SITE } from './studies.js';

const EPOCH = 'genealogy';
const MAX_EVENTS = 60;

const yearLabel = (g) => (g == null ? null : g < 0 ? `${-g} BC` : `AD ${g}`);

export function readYear(input) {
  const text = String(input ?? '')
    .trim()
    .toUpperCase()
    .replace(/\./g, '');
  let m;
  if ((m = /^AM\s*(-?\d+)$/.exec(text)) || (m = /^(-?\d+)\s*AM$/.exec(text))) {
    const am = parseInt(m[1], 10);
    return { am, gregorian: amToGregorian(am, EPOCH) };
  }
  if ((m = /^(\d+)\s*(BC|BCE)$/.exec(text))) return fromGregorian(-parseInt(m[1], 10));
  if ((m = /^(?:AD|CE)\s*(\d+)$/.exec(text)) || (m = /^(\d+)\s*(?:AD|CE)$/.exec(text)))
    return fromGregorian(parseInt(m[1], 10));
  if ((m = /^(-?\d+)$/.exec(text))) return fromGregorian(parseInt(m[1], 10));
  return null;
}

function fromGregorian(g) {
  return { am: gregorianToAm(g, EPOCH), gregorian: g };
}

function describeEvent(e) {
  return {
    id: e.id,
    event: e.label,
    year: yearLabel(e.gregorian),
    am: e.am,
    scripture: e.refs ?? e.scripture,
    note: e.note ?? e.description ?? e.evidence,
    certainty: e.certainty ?? e.tier,
    error_bar: e.error,
    study: e.study_ref ? `${SITE}${e.study_ref}/` : undefined,
  };
}

const EPOCH_NOTE =
  "Dates follow this site's chronology: creation in 3959 BC (AM 0) on the Masoretic numbers, anchored to an Exodus in 1446 BC. Each date carries its certainty; Chronology Anchors explains every anchor. https://the-way.lewy.au/chronology/chronology-anchors/";

export function convertYear({ year }) {
  const y = readYear(year);
  if (!y || y.am == null) throw new Error('Give a year as "1446 BC", "AD 33" or "AM 2513".');
  const day = getMillennialDay(y.am);
  const events = loadEvents().filter((e) => e.am != null);
  const age = [...CHRONOLOGY.ages]
    .map((a) => ({ a, start: a.from_am ?? events.find((e) => e.id === a.from)?.am }))
    .filter((x) => x.start != null && x.start <= y.am)
    .sort((p, q) => q.start - p.start)[0]?.a;
  const nearest = events
    .map((e) => ({ e, d: Math.abs(e.am - y.am) }))
    .sort((p, q) => p.d - q.d)
    .slice(0, 5)
    .map(({ e }) => describeEvent(e));
  return {
    year: yearLabel(y.gregorian),
    am: y.am,
    millennial_day: day
      ? {
          day: day.day,
          note: 'One of the seven thousand-year "days" of 2 Peter 3:8 this site reads history by.',
        }
      : undefined,
    age: age ? { name: age.label, term: age.term, scripture: age.refs } : undefined,
    nearest_events: nearest,
    epoch: EPOCH_NOTE,
  };
}

export function timeline({ from, to, search }) {
  const start = from ? readYear(from) : null;
  const end = to ? readYear(to) : null;
  const words = String(search ?? '')
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  let events = loadEvents().filter((e) => {
    if (start?.am != null && (e.am == null || e.am < start.am)) return false;
    if (end?.am != null && (e.am == null || e.am > end.am)) return false;
    if (words.length) {
      const text = [e.label, e.refs, e.scripture, e.note, e.description, ...(e.people ?? [])]
        .join(' ')
        .toLowerCase();
      if (!words.every((w) => text.includes(w))) return false;
    }
    return true;
  });
  events = events.sort(
    (a, b) => (a.am ?? Infinity) - (b.am ?? Infinity) || (a.hour ?? 0) - (b.hour ?? 0)
  );
  return {
    from: start ? yearLabel(start.gregorian) : undefined,
    to: end ? yearLabel(end.gregorian) : undefined,
    total: events.length,
    events: events.slice(0, MAX_EVENTS).map(describeEvent),
    more: events.length > MAX_EVENTS ? 'Narrow the range or the search for the rest.' : undefined,
    epoch: EPOCH_NOTE,
    timeline: `${SITE}timeline/`,
  };
}

// Adam to Terah store no years of their own; the Masoretic variant supplies them, as on the timeline.
const allPeople = () => mergePeopleWithVariant(loadGenealogyPeople(), 'mt');

function findPerson(name) {
  const people = allPeople();
  const want = String(name ?? '')
    .toLowerCase()
    .trim();
  return (
    people.find((p) => p.id === want || p.name.toLowerCase() === want) ??
    people.find(
      (p) =>
        p.name.toLowerCase().includes(want) ||
        (p.alternate_names ?? []).some((n) => n.toLowerCase().includes(want))
    )
  );
}

// Who else was alive: lifespans overlapping on the site's dates. Genesis's numbers make some of
// these striking (Shem outlives Abraham's birth by 150 years on the Masoretic chain), so the
// overlap is given in years for the reader to check against the verses.
export function person({ name }) {
  const p = findPerson(name);
  if (!p)
    throw new Error(
      `No one named "${name}" in the genealogy. It covers Adam to Jesus along the lines the timeline draws.`
    );
  const people = allPeople();
  const byId = new Map(people.map((x) => [x.id, x]));
  const born = p.zadok_year_born;
  const died = p.zadok_year_died;
  const contemporaries =
    born != null && died != null
      ? people
          .filter((o) => o.id !== p.id && o.zadok_year_born != null && o.zadok_year_died != null)
          .map((o) => ({
            o,
            years: Math.min(died, o.zadok_year_died) - Math.max(born, o.zadok_year_born),
          }))
          .filter((x) => x.years > 0)
          .sort((a, b) => b.years - a.years)
          .slice(0, 12)
          .map(({ o, years }) => ({
            name: o.name,
            born: yearLabel(o.gregorian_year_born),
            died: yearLabel(o.gregorian_year_died),
            years_alive_together: years,
          }))
      : [];
  return {
    name: p.name,
    title: p.title,
    born: born != null ? { year: yearLabel(p.gregorian_year_born), am: born } : undefined,
    died: died != null ? { year: yearLabel(p.gregorian_year_died), am: died } : undefined,
    lifespan: p.lifespan_years ?? (born != null && died != null ? died - born : undefined),
    father: byId.get(p.parent_id)?.name,
    children: (p.children ?? []).map((id) => byId.get(id)?.name ?? id),
    lines: p.lineages,
    name_meaning: p.name_study,
    events: (p.major_events ?? []).map((e) => ({
      event: e.event,
      year: yearLabel(e.gregorian_year),
      scripture: e.refs,
      note: e.description || undefined,
    })),
    alive_at_the_same_time: contemporaries,
    numbers_by_tradition: p.traditions
      ? Object.fromEntries(
          Object.entries(p.traditions).map(([k, t]) => [
            k,
            { age_at_heir: t.age_at_heir_birth, lifespan: t.lifespan_total, verses: t.verses },
          ])
        )
      : undefined,
    note: 'Genesis 5 and 11 give different numbers in the Masoretic text, the Septuagint and the Samaritan Pentateuch; this site follows the Masoretic. The Flood and the King Lists explains why.',
    epoch: EPOCH_NOTE,
  };
}

export function propheticOutline({ topic }) {
  const events = new Map(loadEvents().map((e) => [e.id, e]));
  const want = String(topic ?? '').toLowerCase();
  const match = (...parts) => !want || parts.join(' ').toLowerCase().includes(want);
  const future = CHRONOLOGY.future_sequence;
  return {
    reading:
      "This site's reading is dispensational and pretribulational. Every item carries its certainty: 'stated' means the text gives it; 'site-reading' is this site's reading; 'contested' means the text does not settle it and readings differ. Say which when you pass it on.",
    still_to_come: {
      note: future.note,
      events: future.events
        .filter((e) => match(e.label, e.refs, e.note, e.track))
        .map((e) => ({
          event: e.label,
          track: e.track,
          years_from_the_covenant: e.end != null ? `${e.at} to ${e.end}` : e.at,
          scripture: e.refs,
          certainty: e.certainty,
          note: e.note,
          study: e.study_ref ? `${SITE}${e.study_ref}/` : undefined,
        })),
    },
    daniels_kingdoms: CHRONOLOGY.kingdoms
      .filter((k) => match(k.label, k.image, k.beast, k.note))
      .map((k) => ({
        kingdom: k.label,
        image: k.image,
        image_scripture: k.image_refs,
        beast: k.beast,
        beast_scripture: k.beast_refs,
        named_in: k.named,
        from: yearLabel(events.get(k.from)?.gregorian),
        to: yearLabel(events.get(k.to)?.gregorian),
        certainty: k.certainty,
        note: k.note,
      })),
    threads: CHRONOLOGY.threads
      .filter((t) => match(t.label, t.note, t.refs))
      .map((t) => ({
        thread: t.label,
        scripture: t.refs,
        certainty: t.certainty,
        note: t.note,
        events: t.events
          .map((id) => events.get(id))
          .filter(Boolean)
          .map((e) => `${yearLabel(e.gregorian) ?? 'undated'}: ${e.label}`),
      })),
    milestones: CHRONOLOGY.milestones
      .filter((m) => match(m.label, m.note))
      .map((m) => ({ milestone: m.label, year: yearLabel(m.gregorian_year), note: m.note })),
    timeline: `${SITE}timeline/`,
  };
}
