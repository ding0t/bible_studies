// Shared constants and helpers for the Chronology tool (the Prophetic Timeline and the genealogy
// it now contains). No JSX here.
export const BASE_WIDTH = 1600;
export const ROW_HEIGHT = 26;
export const MARKER_ROW = 18;
// Wider than this and only the anchor table's core rows show; the rest would sit on top of
// one another between Solomon and Christ.
export const CORE_ONLY_SPAN = 3000;
// Narrower than this and each person's recorded events show as their own layer.
export const LIFE_EVENTS_SPAN = 600;

// The site works to one chronology line -- the Masoretic numbers on the genealogical epoch
// (Exodus 1446 BC, creation 3959 BC) -- so only that line is on by default. The others stay
// available as comparisons, labelled as such.
export const VARIANT_META = {
  mt: { label: 'Masoretic Text (this site)', color: '#2563eb' },
  lxx: { label: 'Septuagint (compare)', color: '#7c3aed' },
  sp: { label: 'Samaritan Pentateuch (compare)', color: '#059669' },
};

export const EPOCH_META = {
  genealogy: { color: '#475569' },
  millennial_2075: { color: '#e11d48' },
};

export const LAYER_META = {
  genesis: { label: 'Genesis', color: '#b45309' },
  anchor: { label: 'Anchor table', color: '#0891b2' },
  archaeology: { label: 'Other archaeology', color: '#0f766e' },
  milestone: { label: 'Prophecy', color: '#be185d' },
  life: { label: "People's events", color: '#64748b' },
  event: { label: 'Studies', color: '#65a30d' },
};

// Each period is a range on the Anno Mundi axis, given either directly or as Gregorian years
// converted through the primary epoch. The two future periods have no date at all: Scripture gives
// their lengths and withholds their start, so they are drawn on their own undated axis.
export const PERIODS = [
  { id: 'week', label: 'The whole week', am: [0, 7000] },
  { id: 'creation-flood', label: 'Creation to the Flood', am: [0, 1700] },
  { id: 'flood-abraham', label: 'Flood to Abraham', am: [1600, 2150] },
  { id: 'patriarchs', label: 'Patriarchs to the conquest', am: [2000, 2600] },
  { id: 'conquest-solomon', label: 'Conquest to Solomon', am: [2530, 3060] },
  { id: 'kingdom-exile', label: 'Kingdom, exile and return', greg: [-1000, -500] },
  { id: 'between', label: 'Between the Testaments', greg: [-540, 5] },
  { id: 'christ', label: 'When Jesus was on earth', greg: [-8, 36] },
  // AD 33, hour by hour: hours from midnight at the start of Saturday 28 March (Julian).
  { id: 'passion-week', label: 'Passion week (AD 33)', dated: [42, 222] },
  { id: 'betrayal', label: 'Thursday night: betrayal and trials', dated: [137, 153] },
  { id: 'crucifixion', label: 'Friday: the crucifixion', dated: [150, 163] },
  { id: 'death-resurrection', label: 'Three days and three nights', dated: [132, 214] },
  { id: 'resurrection', label: 'Sunday: the resurrection', dated: [195, 217] },
  { id: 'pentecost', label: 'Passover to Pentecost', dated: [132, 1404] },
  { id: 'church', label: 'The church age', greg: [25, 2050] },
  { id: 'week70', label: "Daniel's 70th week (undated)", future: [-0.8, 7.6] },
  { id: 'millennium', label: 'The millennium and after (undated)', future: [-15, 1025] },
];

export const CERTAINTY_META = {
  stated: { label: 'Stated in the text', opacity: 0.85, dashed: false },
  'site-reading': { label: "This site's reading", opacity: 0.5, dashed: false },
  contested: { label: 'Placement contested', opacity: 0.18, dashed: true },
};

export function formatGregorian(year) {
  if (year === null || year === undefined) return 'unknown';
  return year < 0 ? `${Math.abs(year)} BC` : `AD ${year}`;
}

// "1000 BC", "AD 33", "33", "-1000" -> signed Gregorian year (no year zero), or null.
export function parseGregorian(text) {
  const t = String(text).trim().toUpperCase();
  const m = t.match(/^(AD\s*)?(-?\d+)\s*(BC|BCE|AD|CE)?$/);
  if (!m) return null;
  let n = parseInt(m[2], 10);
  if (m[3] === 'BC' || m[3] === 'BCE') n = -Math.abs(n);
  return n === 0 ? null : n;
}

export function studyUrl(studyRef) {
  return `/${studyRef}/`;
}

export function niceStep(span, targetTicks = 14) {
  const steps = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000];
  return steps.find((s) => span / s <= targetTicks) ?? 1000;
}

// Greedy row assignment so overlapping bars on one track do not draw over each other.
export function stackRows(items, xOf, minGap = 90) {
  const rowsEnd = [];
  return items.map((it) => {
    const x0 = xOf(it.at);
    const x1 = Math.max(x0 + minGap, xOf(it.end ?? it.at) + 4);
    let row = rowsEnd.findIndex((end) => end <= x0);
    if (row === -1) {
      row = rowsEnd.length;
      rowsEnd.push(x1);
    } else rowsEnd[row] = x1;
    return { ...it, row };
  });
}

export const theme = {
  text: 'var(--color-text, #1e293b)',
  textMuted: 'var(--color-text-muted, #64748b)',
  textSubtle: 'var(--color-text-subtle, #475569)',
  bg: 'var(--color-bg, #f8fafc)',
  bgElevated: 'var(--color-bg-elevated, #ffffff)',
  cardBg: 'var(--color-card-bg, #f8fafc)',
  border: 'var(--color-border, #e2e8f0)',
  borderStrong: 'var(--color-border-strong, #cbd5e1)',
  primary: 'var(--color-primary, #3b82f6)',
  selectedBg: 'var(--color-selected-bg, #eef2ff)',
  calloutBg: 'var(--color-callout-bg, #f0f9ff)',
};

export const chip = (active, color) => ({
  padding: '0.4rem 0.75rem',
  borderRadius: '999px',
  border: `1.5px solid ${active ? color : theme.border}`,
  background: active ? `${color}1a` : theme.cardBg,
  color: active ? color : theme.textMuted,
  fontWeight: active ? 700 : 500,
  fontSize: '0.8rem',
  cursor: 'pointer',
  whiteSpace: 'nowrap',
});

export const sectionLabel = {
  fontSize: '0.75rem',
  fontWeight: 700,
  color: theme.textMuted,
  marginBottom: '0.4rem',
};

// Which published study backs a person's dates. Adam-Terah come from the manuscript comparison in
// Genealogy and Times; from Egypt to David, Four Hundred and Eighty Years (the priestly and Davidic
// lines, and Caleb's ages behind the conquest); the rail from Solomon on is Chronology Anchors.
// Site-absolute: the site is served from its domain root.
const GENEALOGY_TIMES_URL = '/chronology/genealogy-times/';
const CHRONOLOGY_ANCHORS_URL = '/chronology/chronology-anchors/';
const FOUR_EIGHTY_URL = '/chronology/four-hundred-and-eighty-years/';
const PRIESTLY_LINE = {
  url: `${FOUR_EIGHTY_URL}#genealogy-check-1-the-priestly-line-broadly-consistent-with-480-years`,
  label: 'Four Hundred and Eighty Years: the priestly line from Aaron',
};
const CONQUEST = {
  url: `${FOUR_EIGHTY_URL}#the-problem-the-numbers-dont-add-up-to-480`,
  label: "Four Hundred and Eighty Years: Caleb's ages and the conquest",
};
// Jacob enters Egypt in AM 2298; David is born in AM 2918.
const EGYPT_TO_DAVID = [2298, 2918];
const STUDY_LINKS = {
  methuselah: {
    url: `${GENEALOGY_TIMES_URL}#methuselah-the-name-the-number-and-the-flood`,
    label: 'Methuselah: the name, the number, and the Flood',
  },
  terah: {
    url: `${GENEALOGY_TIMES_URL}#terah-and-abram-a-puzzle-two-different-ways`,
    label: 'Terah and Abram: a puzzle two different ways',
  },
  cainan_gen11: { url: `${GENEALOGY_TIMES_URL}#the-cainan-question`, label: 'The Cainan question' },
  aaron: PRIESTLY_LINE,
  moses: PRIESTLY_LINE,
  elisheba: PRIESTLY_LINE,
  joshua: CONQUEST,
  caleb: CONQUEST,
  jesus: {
    url: `${CHRONOLOGY_ANCHORS_URL}#settling-the-crucifixion-year`,
    label: 'Settling the crucifixion year',
  },
};
export function studyLinkFor(person) {
  if (!person) return null;
  if (STUDY_LINKS[person.id]) return STUDY_LINKS[person.id];
  const born = person.zadok_year_born;
  if (typeof born === 'number' && born >= EGYPT_TO_DAVID[0] && born < EGYPT_TO_DAVID[1]) {
    return {
      url: `${FOUR_EIGHTY_URL}#genealogy-check-2-the-davidic-line-in-real-tension-with-480-years`,
      label: "Four Hundred and Eighty Years: the Davidic line and where Ruth's list telescopes",
    };
  }
  if (typeof person.zadok_year_born === 'number' && person.zadok_year_born < 2513) {
    return {
      url: GENEALOGY_TIMES_URL,
      label: 'Genealogy and Times: the manuscript comparison behind these dates',
    };
  }
  return {
    url: CHRONOLOGY_ANCHORS_URL,
    label: 'Chronology Anchors: what dates this era, and how tightly',
  };
}

// What each data classification means for the reader, and how its bar is drawn.
export const CLASSIFICATION = {
  ACTUAL: { label: 'Stated in Scripture', hatched: false },
  CALCULATED: { label: 'Calculated from stated figures', hatched: true },
  EXTRAPOLATED: { label: 'Estimated: Scripture gives no figure', hatched: true },
};

CLASSIFICATION.TEXTUAL_VARIANT = { label: 'In one manuscript tradition only', hatched: true };

// A marker's date as a reader wants it: the stored year with its error bar or bracket, else the
// Gregorian reading of its Anno Mundi year on the given epoch.
export function markerDateFor(m, epochId, amToGregorian) {
  if (m.gregorian_year != null) {
    const err = m.error?.startsWith('±') ? ` ${m.error}` : '';
    const range = m.error && /\d-\d/.test(m.error) ? ` (${m.error})` : '';
    return `${formatGregorian(m.gregorian_year)}${err}${range}`;
  }
  const g = formatGregorian(amToGregorian(m.am, epochId));
  if (m.amTo != null && m.amTo !== m.am)
    return `${g} – ${formatGregorian(amToGregorian(m.amTo, epochId))}`;
  return g;
}

// Which marker layer an event from loadEvents() belongs to.
export const SOURCE_LAYER = {
  genesis: 'genesis',
  anchor: 'anchor',
  archaeology: 'archaeology',
  milestone: 'milestone',
  passion: 'milestone',
  life: 'life',
};
