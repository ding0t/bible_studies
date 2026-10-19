// The logic behind the Scripture Links explorer and its diagrams, kept apart from the components so
// it can be tested against the real data. Everything here derives from docs/data/scripture-links.json
// (`links`, `methodOrder`), so the diagrams change when export_links.py is re-run and nothing else
// has to be touched. A method the data carries but METHODS does not know would vanish from every
// diagram without a trace, so scriptureLinks.test.js fails on one.
import { BOOK_ORDER, bookName, parseRef } from './scriptureRefs.js';

// `color` is a CSS variable set in tools.css for light and dark. `dash` makes each method readable
// without colour: a printed or colour-blind reader still tells a quotation from an allusion.
export const METHODS = {
  'quotation-greek': {
    label: 'Quotation',
    weight: 'textual fact',
    why: 'Greek on both sides. The New Testament authors read their Old Testament in Greek, so the quotation is literally the same words.',
    verb: ['quotes', 'quoted by'],
    color: 'var(--color-link-quotation, #1d4ed8)',
    dash: null,
    width: 2.4,
  },
  'inner-biblical': {
    label: 'Quotation',
    weight: 'textual fact',
    why: 'Hebrew on both sides, with no translation in between: the Old Testament quoting itself.',
    verb: ['quotes', 'quoted by'],
    color: 'var(--color-link-inner, #047857)',
    dash: null,
    width: 1.4,
  },
  'allusion-lemma': {
    label: 'Allusion',
    weight: 'shared rare vocabulary',
    why: 'No shared phrasing. What these passages share is vocabulary that occurs almost nowhere else.',
    verb: ['echoes', 'echoed by'],
    color: 'var(--color-link-allusion, #b45309)',
    dash: '6 3',
    width: 1.8,
  },
  'quotation-crosslang': {
    label: 'Quotation',
    weight: 'read against the Hebrew',
    why: 'The Greek of the New Testament verse matches the Hebrew of the Old, word for word in meaning, through the vocabulary the Septuagint translators themselves chose. Only in verses that cite Scripture: it finds quotations that follow the Hebrew where the Greek Old Testament reads differently.',
    verb: ['quotes', 'quoted by'],
    color: 'var(--color-link-crosslang, #7c3aed)',
    dash: '8 2 2 2',
    width: 2,
  },
  'quotation-hebrew': {
    label: 'Candidate',
    weight: "a translator's judgement",
    why: 'A 19th-century Hebrew New Testament renders this as a quotation. That is an informed reading of the text, not evidence from it, and worth checking in Greek.',
    verb: ['may quote', 'may be quoted by'],
    color: 'var(--color-link-candidate, #be123c)',
    dash: '1.5 3.5',
    width: 2,
  },
};

// Beside its label, a method that is a quotation in Hebrew says so, since two methods share a label.
export const METHOD_NAMES = {
  'quotation-greek': 'Quotation (Greek)',
  'inner-biblical': 'Quotation (Hebrew)',
  'quotation-crosslang': 'Quotation (from the Hebrew)',
  'allusion-lemma': 'Allusion',
  'quotation-hebrew': 'Candidate',
};

// What each rule in the build means, in plain words, for the "found by" line under a link.
export const BASIS = {
  alignment: 'the wording lines up',
  'unique-phrases': 'phrases found in only one Old Testament verse',
  'formula+phrases': 'the verse cites Scripture and shares a phrase found in only one Old Testament verse',
  lemma: 'the same words, matched on their dictionary forms',
  'lemma-run': 'one of a run of parallel verses',
  crosslang: 'the Greek matches the Hebrew through the Septuagint’s own vocabulary',
  'rare-lemmas': 'shared rare words',
  'hebrew-nt': 'a Hebrew translation of the New Testament renders it as a quotation',
};

export const basisWords = (basis) =>
  (basis ? basis.split('+').reduce((parts, b, i, all) => {
    // 'formula+phrases' is one rule written with a plus; join it back before translating.
    if (b === 'formula' && all[i + 1] === 'phrases') return parts;
    const key = b === 'phrases' && all[i - 1] === 'formula' ? 'formula+phrases' : b;
    if (BASIS[key]) parts.push(BASIS[key]);
    return parts;
  }, []) : []);

export const SCOPES = [
  { id: 'nt-ot', label: 'New Testament and the Old', test: (f, t) => isNT(f) && !isNT(t) },
  { id: 'ot-ot', label: 'Old Testament parallels', test: (f, t) => !isNT(f) && !isNT(t) },
  { id: 'all', label: 'Everything', test: () => true },
];

// The Septuagint's extra books sit in the data (a New Testament verse can echo Wisdom or 4 Maccabees)
// but not in the canon list: they are placed after the Old Testament and named in full.
const APOCRYPHA = {
  Tob: 'Tobit', TobS: 'Tobit', Jdt: 'Judith', Wis: 'Wisdom', Sir: 'Sirach', Bar: '1 Baruch', '1Esd': '1 Esdras',
  '2Esd': '2 Esdras', '1Macc': '1 Maccabees', '2Macc': '2 Maccabees', '3Macc': '3 Maccabees', '4Macc': '4 Maccabees',
  PsSol: 'Psalms of Solomon', JoshB: 'Joshua (Codex B)', EpJer: 'Letter of Jeremiah', PrMan: 'Prayer of Manasseh',
};
const EXTRA = Object.keys(APOCRYPHA);
const FIRST_NT = BOOK_ORDER.indexOf('Matt');
export const bookOrder = (book) => {
  const at = BOOK_ORDER.indexOf(book);
  if (at >= 0) return at;
  return FIRST_NT - 0.5 + (Math.max(0, EXTRA.indexOf(book)) + 1) / 100;
};
export const isNT = (book) => bookOrder(book) >= FIRST_NT;
export const displayBook = (book) => APOCRYPHA[book] ?? bookName(book);

export const bookOfKey = (key) => key.slice(0, key.lastIndexOf(' '));
export const chapterOfKey = (key) => key.slice(0, key.lastIndexOf(':'));

// What a reader typed ("Hebrews 10:5", "heb 10.5", "Ps 40") as the data's own key. A chapter has
// no verse and is matched as a prefix, so "Isaiah 53" finds the links anywhere in the chapter.
export function lookupKey(text) {
  const typed = String(text ?? '').trim().replace(/(\d)\.(\d)/g, '$1:$2').replace(/^(\d?\s*)([a-z])/, (_, n, c) => n + c.toUpperCase());
  let ref = parseRef(typed);
  // "Ps 40": an abbreviation without a verse is not a reference in prose, but it is one in a search box.
  if (!ref) {
    const bare = typed.match(/^(.+?)\s+(\d{1,3})$/);
    const asVerse = bare && parseRef(`${bare[1]} ${bare[2]}:1`);
    if (asVerse) ref = { book: asVerse.book, c1: asVerse.c1 };
  }
  if (!ref) return null;
  if (ref.v1 === undefined) return { chapter: `${ref.book} ${ref.c1}`, label: `${bookName(ref.book)} ${ref.c1}` };
  return { key: `${ref.book} ${ref.c1}:${ref.v1}`, label: `${bookName(ref.book)} ${ref.c1}:${ref.v1}` };
}

export const prettyKey = (key) => {
  const book = bookOfKey(key);
  return `${displayBook(book)} ${key.slice(book.length + 1)}`;
};

export function inScope(link, scopeId) {
  const scope = SCOPES.find((s) => s.id === scopeId) ?? SCOPES[2];
  return scope.test(bookOfKey(link.f), bookOfKey(link.t));
}

// Every verse a link touches, mapped to its links. `te` is the English-numbered twin of a
// Hebrew-numbered verse (Psalm 40:6 and 40:7), so a reader using either number finds it.
export function indexByRef(links) {
  const map = new Map();
  const add = (key, entry) => {
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(entry);
  };
  for (const link of links) {
    add(link.f, { link, direction: 'from' });
    add(link.t, { link, direction: 'to' });
    if (link.te && link.te !== link.t) add(link.te, { link, direction: 'to' });
  }
  return map;
}

export function entriesFor(byRef, target) {
  if (target.key) return (byRef.get(target.key) ?? []).map((e) => ({ ...e, at: target.key }));
  const out = [];
  for (const [key, entries] of byRef) {
    if (chapterOfKey(key) === target.chapter) for (const e of entries) out.push({ ...e, at: key });
  }
  return out;
}

// Book to book, per method: how many links run from one book to another.
export function bookFlows(links) {
  const flows = new Map();
  for (const l of links) {
    const id = `${bookOfKey(l.f)}>${bookOfKey(l.t)}>${l.m}`;
    const hit = flows.get(id) ?? { from: bookOfKey(l.f), to: bookOfKey(l.t), m: l.m, links: [] };
    hit.links.push(l);
    flows.set(id, hit);
  }
  return [...flows.values()];
}

// Books in canonical order that have a link on either side, with how many.
export function bookDegrees(links) {
  const degree = new Map();
  for (const l of links) {
    for (const b of [bookOfKey(l.f), bookOfKey(l.t)]) degree.set(b, (degree.get(b) ?? 0) + 1);
  }
  return [...degree]
    .map(([book, n]) => ({ book, n }))
    .sort((a, b) => bookOrder(a.book) - bookOrder(b.book));
}

export function matrix(links) {
  const rows = [...new Set(links.map((l) => bookOfKey(l.f)))].sort((a, b) => bookOrder(a) - bookOrder(b));
  const cols = [...new Set(links.map((l) => bookOfKey(l.t)))].sort((a, b) => bookOrder(a) - bookOrder(b));
  const cells = new Map();
  for (const l of links) {
    const id = `${bookOfKey(l.f)}>${bookOfKey(l.t)}`;
    if (!cells.has(id)) cells.set(id, []);
    cells.get(id).push(l);
  }
  return { rows, cols, cells };
}

export function methodBreakdown(links, methodOrder) {
  return methodOrder.map((m) => {
    const mine = links.filter((l) => l.m === m);
    const listed = mine.filter((l) => l.c).length;
    return { m, total: mine.length, listed, found: mine.length - listed };
  });
}

// The verses most often on the receiving end: what the rest of Scripture keeps returning to.
export function topTargets(links, n = 10) {
  const count = new Map();
  for (const l of links) count.set(l.t, (count.get(l.t) ?? 0) + 1);
  return [...count]
    .map(([key, total]) => ({ key, total }))
    .sort((a, b) => b.total - a.total || bookOrder(bookOfKey(a.key)) - bookOrder(bookOfKey(b.key)))
    .slice(0, n);
}

// Verses worth opening first: the ones with both a quotation and something the reference lists miss.
export function startingPoints(links, n = 6) {
  const score = new Map();
  for (const l of links) {
    if (l.m !== 'quotation-greek' && l.m !== 'allusion-lemma') continue;
    const s = score.get(l.f) ?? { quote: 0, found: 0 };
    s.quote += 1;
    if (!l.c) s.found += 1;
    score.set(l.f, s);
  }
  return [...score]
    .filter(([, s]) => s.found > 0)
    .sort((a, b) => b[1].quote - a[1].quote || b[1].found - a[1].found)
    .slice(0, n)
    .map(([key]) => key);
}
