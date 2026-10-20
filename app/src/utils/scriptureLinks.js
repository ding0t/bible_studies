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

// Each rule as the method page profiles it: what it sees, what only it can do, where it goes wrong,
// with a case of each a reader can open. The numbers beside these come from link-method.json, so the
// profile stays editorial and the counts stay live. `method` picks the colour; `dash` tells a rule
// from its siblings in the same class. Weak examples are links the rule really admits that no
// outside list confirms, or quotations it really misses.
export const RULES = [
  {
    id: 'greek-alignment', method: 'quotation-greek', dash: null, name: 'Wording that lines up',
    sees: 'About nine Greek words in order, allowing for words added or left out.',
    strong: 'Long and adapted quotations: Luke 4:18 leaves a clause out of Isaiah 61:1 and still aligns.',
    strongRef: 'Luke 4:18',
    weak: 'Refrains and stock phrases align too: Mark 12:30 against seven verses of Deuteronomy, Acts 4:24 against Haggai 2:6.',
    weakRef: 'Acts 4:24',
  },
  {
    id: 'greek-unique-phrases', method: 'quotation-greek', dash: '5 3', name: 'A phrase found in one verse',
    sees: 'Three-word phrases that occur in only one Septuagint verse.',
    strong: 'Short quotations made of everyday words, which no rarity measure sees: John 10:34 and Psalm 82:6.',
    strongRef: 'John 10:34',
    weak: 'A phrase can be unique and still be idiom: Ephesians 6:10’s “the strength of his might” and Daniel 4:30.',
    weakRef: 'Eph 6:10',
  },
  {
    id: 'greek-formula', method: 'quotation-greek', dash: '1.5 3', name: 'The verse cites Scripture',
    sees: '“It is written”, “the Scripture”, “that it might be fulfilled”, plus two unique phrases.',
    strong: 'The short, famous quotations: James 2:8, Romans 1:17, Matthew 4:7, Matthew 2:6 from Micah.',
    strongRef: 'Jas 2:8',
    weak: 'Only where the writer says he is quoting. Romans 4:3 says it and is missed: its phrase also stands in Psalm 106:31.',
    weakRef: 'Rom 4:3',
  },
  {
    id: 'quotation-crosslang', method: 'quotation-crosslang', dash: '8 2 2 2', name: 'Greek read against the Hebrew',
    sees: 'The Greek verse against the Hebrew, through the Septuagint translators’ own word choices.',
    strong: 'Quotations that follow the Hebrew where the Septuagint differs: 1 Corinthians 15:54 and Isaiah 25:8.',
    strongRef: '1Cor 15:54',
    weak: 'It takes the best match it can find: John 19:29’s sour wine lands on Ruth 2:14.',
    weakRef: 'John 19:29',
  },
  {
    id: 'allusion-lemma', method: 'allusion-lemma', dash: '6 3', name: 'Shared rare words',
    sees: 'Words found in 30 verses or fewer, shared by two passages with no phrase in common.',
    strong: 'Echoes with no shared phrasing: the jewels of Revelation 21:20 and Ezekiel 28:13.',
    strongRef: 'Rev 21:20',
    weak: 'Mostly lists: names in the genealogies, places, gems and spices.',
    weakRef: 'Luke 3:35',
  },
  {
    id: 'quotation-hebrew', method: 'quotation-hebrew', dash: '1.5 3.5', name: 'A Hebrew New Testament',
    sees: 'Where Delitzsch’s 19th-century Hebrew translation uses the Old Testament’s own words.',
    strong: 'Almost always confirmed, and it catches quotations the Greek method misses.',
    strongRef: 'Acts 2:20',
    weak: 'A translator’s judgement: he knew the tradition, so agreeing with the lists proves little.',
    weakRef: null,
  },
  {
    id: 'hebrew-alignment', method: 'inner-biblical', dash: null, name: 'Hebrew wording lines up',
    sees: 'Hebrew words in order, as printed.',
    strong: 'Near-verbatim retellings: Kings in Chronicles, Isaiah 36-39 in 2 Kings 18-20.',
    strongRef: '2Chr 36:22',
    weak: 'On its own it finds formulas (“the rest of the acts of…”), so it admits nothing without the dictionary-form match.',
    weakRef: null,
  },
  {
    id: 'hebrew-lemma', method: 'inner-biblical', dash: '5 3', name: 'Same words in dictionary form',
    sees: 'Hebrew words reduced to their dictionary forms, rare ones weighted more.',
    strong: 'Parallels the printed text cannot match, where a word is spelled or prefixed differently: 2 Samuel 22 and Psalm 18.',
    strongRef: '2Sam 22:3',
    weak: 'Short verses carry too little to score: “You shall not murder” is two Hebrew words.',
    weakRef: 'Exod 20:13',
  },
  {
    id: 'hebrew-lemma-run', method: 'inner-biblical', dash: '1.5 3', name: 'One of a run',
    sees: 'A weaker match whose neighbouring verses also match, as borrowed passages come in runs.',
    strong: 'Whole borrowed passages: 1 Chronicles 16:8 and Psalm 105:1 begin a psalm the Chronicler copies verse after verse.',
    strongRef: '1Chr 16:8',
    weak: 'A weak verse is admitted on its neighbours’ strength, so it is confirmed least often.',
    weakRef: null,
  },
];

export const ruleById = Object.fromEntries(RULES.map((r) => [r.id, r]));

// How often links found the way this one was found are confirmed by an outside list, from the
// exported links themselves: grouped by class and the exact rules that admitted them.
export function calibration(links) {
  const out = new Map();
  for (const l of links) {
    for (const id of [`${l.m}|${l.b}`, l.m]) {
      const s = out.get(id) ?? { n: 0, c: 0 };
      s.n += 1;
      s.c += l.c;
      out.set(id, s);
    }
  }
  return out;
}

// A group under ten links says little about itself; fall back to the class as a whole.
export function confirmationFor(cal, link) {
  const exact = cal.get(`${link.m}|${link.b}`);
  return exact && exact.n >= 10 ? { ...exact, exact: true } : { ...cal.get(link.m), exact: false };
}

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
