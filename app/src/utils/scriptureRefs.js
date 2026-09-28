// Finds Bible references in running prose for the verse pop-ups. Book codes are the OSIS-style
// ones bible-text.db uses (Gen, Ps, 1Cor), because the exported verse files are named by them.
//
// Written as prose, a reference is rarely one clean "Book ch:v". Studies write "Romans 8:28, 30;
// 9:1", "Jude 6", "vv. 3-5". This module turns each of those into its own clickable span, and
// leaves a bare "vv. 3-5" as a relative reference for the page script to resolve against the
// passage the reader is already in.

// [osis, full names..., abbreviations...]. A full name matches "Romans 8" as a whole chapter; an
// abbreviation must carry chapter:verse ("Ex 3:14"), because "Ex 2" or "Is 5" in prose is more
// often not a reference at all.
const BOOKS = [
  ['Gen', ['Genesis'], ['Gen', 'Ge', 'Gn']],
  ['Exod', ['Exodus'], ['Exod', 'Exo', 'Ex']],
  ['Lev', ['Leviticus'], ['Lev', 'Le', 'Lv']],
  ['Num', ['Numbers'], ['Num', 'Nu', 'Nm']],
  ['Deut', ['Deuteronomy'], ['Deut', 'Deu', 'Dt']],
  ['Josh', ['Joshua'], ['Josh', 'Jos']],
  ['Judg', ['Judges'], ['Judg', 'Jdg', 'Jg']],
  ['Ruth', ['Ruth'], ['Rut', 'Ru']],
  ['1Sam', ['1 Samuel', 'I Samuel', 'First Samuel'], ['1 Sam', '1Sam', '1Sa', '1 Sa']],
  ['2Sam', ['2 Samuel', 'II Samuel', 'Second Samuel'], ['2 Sam', '2Sam', '2Sa', '2 Sa']],
  ['1Kgs', ['1 Kings', 'I Kings', 'First Kings'], ['1 Kgs', '1Kgs', '1Ki', '1 Ki', '1 Kin']],
  ['2Kgs', ['2 Kings', 'II Kings', 'Second Kings'], ['2 Kgs', '2Kgs', '2Ki', '2 Ki', '2 Kin']],
  ['1Chr', ['1 Chronicles', 'I Chronicles'], ['1 Chr', '1Chr', '1Ch', '1 Ch', '1 Chron']],
  ['2Chr', ['2 Chronicles', 'II Chronicles'], ['2 Chr', '2Chr', '2Ch', '2 Ch', '2 Chron']],
  ['Ezra', ['Ezra'], ['Ezr']],
  ['Neh', ['Nehemiah'], ['Neh', 'Ne']],
  ['Esth', ['Esther'], ['Esth', 'Est', 'Es']],
  ['Job', ['Job'], ['Jb']],
  ['Ps', ['Psalms', 'Psalm'], ['Pss', 'Psa', 'Ps', 'Psm']],
  ['Prov', ['Proverbs'], ['Prov', 'Pro', 'Pr', 'Prv']],
  ['Eccl', ['Ecclesiastes', 'Qoheleth'], ['Eccl', 'Ecc', 'Ec', 'Qoh']],
  ['Song', ['Song of Songs', 'Song of Solomon', 'Canticles'], ['Song', 'Sng', 'SS']],
  ['Isa', ['Isaiah'], ['Isa']],
  ['Jer', ['Jeremiah'], ['Jer', 'Je']],
  ['Lam', ['Lamentations'], ['Lam', 'La']],
  ['Ezek', ['Ezekiel'], ['Ezek', 'Eze', 'Ezk']],
  ['Dan', ['Daniel'], ['Dan', 'Da', 'Dn']],
  ['Hos', ['Hosea'], ['Hos', 'Ho']],
  ['Joel', ['Joel'], ['Joe', 'Jl']],
  ['Amos', ['Amos'], ['Amo']],
  ['Obad', ['Obadiah'], ['Obad', 'Oba', 'Ob']],
  ['Jonah', ['Jonah'], ['Jon', 'Jnh']],
  ['Mic', ['Micah'], ['Mic', 'Mi']],
  ['Nah', ['Nahum'], ['Nah', 'Na']],
  ['Hab', ['Habakkuk'], ['Hab']],
  ['Zeph', ['Zephaniah'], ['Zeph', 'Zep']],
  ['Hag', ['Haggai'], ['Hag']],
  ['Zech', ['Zechariah'], ['Zech', 'Zec']],
  ['Mal', ['Malachi'], ['Mal']],
  ['Matt', ['Matthew'], ['Matt', 'Mat', 'Mt']],
  ['Mark', ['Mark'], ['Mar', 'Mk', 'Mrk']],
  ['Luke', ['Luke'], ['Luk', 'Lk']],
  ['John', ['John'], ['Joh', 'Jn', 'Jhn']],
  ['Acts', ['Acts'], ['Act']],
  ['Rom', ['Romans'], ['Rom', 'Ro', 'Rm']],
  ['1Cor', ['1 Corinthians', 'I Corinthians', 'First Corinthians'], ['1 Cor', '1Cor', '1Co', '1 Co']],
  ['2Cor', ['2 Corinthians', 'II Corinthians', 'Second Corinthians'], ['2 Cor', '2Cor', '2Co', '2 Co']],
  ['Gal', ['Galatians'], ['Gal', 'Ga']],
  ['Eph', ['Ephesians'], ['Eph']],
  ['Phil', ['Philippians'], ['Phil', 'Php', 'Pp']],
  ['Col', ['Colossians'], ['Col']],
  ['1Thess', ['1 Thessalonians', 'I Thessalonians'], ['1 Thess', '1Thess', '1Th', '1 Th', '1 Thes']],
  ['2Thess', ['2 Thessalonians', 'II Thessalonians'], ['2 Thess', '2Thess', '2Th', '2 Th', '2 Thes']],
  ['1Tim', ['1 Timothy', 'I Timothy'], ['1 Tim', '1Tim', '1Ti', '1 Ti']],
  ['2Tim', ['2 Timothy', 'II Timothy'], ['2 Tim', '2Tim', '2Ti', '2 Ti']],
  ['Titus', ['Titus'], ['Tit']],
  ['Phlm', ['Philemon'], ['Phlm', 'Phm']],
  ['Heb', ['Hebrews'], ['Heb']],
  ['Jas', ['James'], ['Jas', 'Jam', 'Jm']],
  ['1Pet', ['1 Peter', 'I Peter', 'First Peter'], ['1 Pet', '1Pet', '1Pe', '1 Pe', '1Pt', '1 Pt']],
  ['2Pet', ['2 Peter', 'II Peter', 'Second Peter'], ['2 Pet', '2Pet', '2Pe', '2 Pe', '2Pt', '2 Pt']],
  ['1John', ['1 John', 'I John', 'First John'], ['1 Jn', '1Jn', '1Jo', '1 Jo', '1John', '1 Joh']],
  ['2John', ['2 John', 'II John', 'Second John'], ['2 Jn', '2Jn', '2Jo', '2 Jo', '2John']],
  ['3John', ['3 John', 'III John', 'Third John'], ['3 Jn', '3Jn', '3Jo', '3 Jo', '3John']],
  ['Jude', ['Jude'], ['Jud']],
  ['Rev', ['Revelation'], ['Rev', 'Re', 'Rv']],
];

// Books of one chapter, where "Jude 6" is verse 6.
const SINGLE_CHAPTER = new Set(['Obad', 'Phlm', '2John', '3John', 'Jude']);

export const BOOK_ORDER = BOOKS.map(([osis]) => osis);
const DISPLAY = Object.fromEntries(BOOKS.map(([osis, names]) => [osis, names[0]]));
const ALIAS = new Map();
for (const [osis, names, abbrevs] of BOOKS) {
  for (const name of names) ALIAS.set(name.toLowerCase(), { osis, strict: false });
  for (const abbrev of abbrevs) {
    const key = abbrev.toLowerCase();
    if (!ALIAS.has(key)) ALIAS.set(key, { osis, strict: true });
  }
}

const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const names = [...ALIAS.keys()].sort((a, b) => b.length - a.length).map((n) => escape(n).replace(/ /g, '\\s+'));

// Book, optional period, chapter, then :verse, a range, or a cross-chapter range. The negative
// lookbehind keeps "Gen" out of "Genesis"-like words and a digit off the front of "1 John".
const DASH = '\\s*[-\u2013\u2014]\\s*';
const FULL = new RegExp(
  `(?<![\\w\u00C0-\u024F])(${names.join('|')})\\.?\\s+(\\d{1,3})(?::(\\d{1,3})(?:${DASH}(\\d{1,3})(?::(\\d{1,3}))?)?|${DASH}(\\d{1,3})(?!:))?(?![\\d:])`,
  'gi'
);

const AT = new RegExp(FULL.source, 'iy');

// A continuation after a reference: "Romans 8:28, 30" or "Romans 8:28; 9:1-4" or "John 1:1, 14".
const NEXT = new RegExp(`^(\\s*[,;]\\s*(?:and\\s+)?)(\\d{1,3})(?::(\\d{1,3}))?(?:${DASH}(\\d{1,3})(?::(\\d{1,3}))?)?(?![\\d:])`);

// "v. 20", "vv. 3-5", "verse 20", "verses 3-5": relative to the passage in hand.
const RELATIVE = new RegExp(`(?<![\\w])(vv?\\.|verses?)\\s*(\\d{1,3})(?:${DASH}(\\d{1,3}))?(?![\\d:])`, 'gi');

// "(5:1)", "at 4:16", "5:6-8": a chapter and verse whose book is the passage in hand.
const BARE = new RegExp(`(?<![\\w:.\u2013/-])(\\d{1,3}):(\\d{1,3})(?:${DASH}(\\d{1,3})(?::(\\d{1,3}))?)?(?![\\d:])`, 'g');
// A chapter and verse straight after a capitalised name belongs to a work the book list does not know
// -- "Tobit 8:19", "m. Avot 3:2, 3:6", "1QS 8:1" -- and is never given a Bible book. The
// capitalised English words a sentence can open with are the exception.
const NAMED = /(?:^|[^\w'’])(\d*[A-Z][\w'’]*)\.?\s*[\u2014\u2013]?\s+(?:\d{1,3}:\d{1,3}(?:\s*[-\u2013]\s*\d{1,3}(?::\d{1,3})?)?\s*(?:[,;]|and)\s*)*$/;
const SENTENCE_START = new Set(
  'In At See Cf Compare From And Then Also Both So But Of On To By After Before Until With Verse Verses Chapter Here There Where When Note Notes Ch'.split(' ')
);

// Whether a bare chapter and verse at the end of `before` belongs to a named non-biblical work.
export function namedWork(before) {
  const named = NAMED.exec(before);
  return Boolean(named && !SENTENCE_START.has(named[1]) && !ALIAS.has(named[1].toLowerCase()));
}

// A book named in words, "three times in Revelation (9:21; 18:23)" or "Hebrews says", is the book a
// bare chapter and verse after it belongs to. Full names only, capitalised, and never one followed by
// a number, which is a reference findRefs already has.
const BOOK_WORD = new RegExp(
  `(?<![\\w\u00C0-\u024F])(${BOOKS.flatMap(([, full]) => full)
    .sort((a, b) => b.length - a.length)
    .map((n) => escape(n).replace(/ /g, '\\s+'))
    .join('|')})(?:'s|’s)?(?![\\w\u00C0-\u024F])(?!\\.?\\s*\\d)`,
  'g'
);

export function findBookNames(text) {
  const out = [];
  BOOK_WORD.lastIndex = 0;
  let m;
  while ((m = BOOK_WORD.exec(text))) {
    const alias = ALIAS.get(m[1].toLowerCase().replace(/\s+/g, ' '));
    if (alias) out.push({ start: m.index, end: m.index + m[0].length, book: alias.osis });
  }
  return out;
}

const int = (s) => (s === undefined ? undefined : parseInt(s, 10));

function make(osis, c1, v1, c2, v2) {
  if (SINGLE_CHAPTER.has(osis) && v1 === undefined && c1 !== 1) {
    // "Jude 6" or "Jude 3-4": the number is a verse.
    return { book: osis, c1: 1, v1: c1, c2: 1, v2: c2 ?? c1 };
  }
  if (v1 === undefined) return { book: osis, c1, v1: undefined, c2: c2 ?? c1, v2: undefined };
  return { book: osis, c1, v1, c2: c2 ?? c1, v2: v2 ?? v1 };
}

// Parse one reference string, e.g. frontmatter's "Ruth 3:9-13" or a data-ref="Gen 7:11".
export function parseRef(text) {
  if (!text) return null;
  const found = findRefs(String(text).trim());
  return found.length && found[0].start === 0 ? found[0].ref : null;
}

// Every reference in a run of text, as {start, end, ref}. Relative references ("vv. 3-5") come back
// with ref.book undefined; the caller decides what they are relative to.
export function findRefs(text) {
  const out = [];
  FULL.lastIndex = 0;
  let m;
  while ((m = FULL.exec(text))) {
    const alias = ALIAS.get(m[1].toLowerCase().replace(/\s+/g, ' '));
    if (!alias) continue;
    const hasVerse = m[3] !== undefined;
    if (alias.strict && !hasVerse) continue;
    // A full name must start with a capital: "job 3" or "mark 4" in prose is a noun.
    if (!/^[1-3IF]?\s*[A-Z]/.test(m[1])) continue;
    const c1 = int(m[2]);
    let ref;
    if (hasVerse) {
      const [a, b] = [int(m[4]), int(m[5])];
      ref = b !== undefined ? make(alias.osis, c1, int(m[3]), a, b) : make(alias.osis, c1, int(m[3]), c1, a);
    } else {
      ref = make(alias.osis, c1, undefined, int(m[6]), undefined);
    }
    out.push({ start: m.index, end: m.index + m[0].length, ref });

    // Walk the continuations: each becomes its own span, inheriting the book, and the chapter
    // too when it gives only a verse.
    let pos = m.index + m[0].length;
    let last = ref;
    for (;;) {
      const rest = text.slice(pos);
      const n = NEXT.exec(rest);
      if (!n) break;
      const numberAt = pos + n[1].length;
      // "Luke 2:1, 2 Corinthians 5" -- the 2 starts the next book, not a verse.
      AT.lastIndex = 0;
      if (AT.test(text.slice(numberAt))) break;
      const semicolon = n[1].includes(';');
      let next;
      if (n[3] !== undefined) {
        const [c, v] = [int(n[2]), int(n[3])];
        next = n[5] !== undefined ? make(last.book, c, v, int(n[4]), int(n[5])) : make(last.book, c, v, c, int(n[4]));
      } else if (last.v1 !== undefined && !semicolon) {
        next = make(last.book, last.c2, int(n[2]), last.c2, int(n[4]));
      } else if (last.v1 === undefined || SINGLE_CHAPTER.has(last.book)) {
        next = SINGLE_CHAPTER.has(last.book)
          ? make(last.book, 1, int(n[2]), 1, int(n[4]))
          : make(last.book, int(n[2]), undefined, int(n[4]), undefined);
      } else {
        break; // "Romans 8:28; 30" is too ambiguous to guess at
      }
      out.push({ start: numberAt, end: pos + n[0].length, ref: next });
      last = next;
      pos += n[0].length;
    }
    FULL.lastIndex = pos;
  }

  RELATIVE.lastIndex = 0;
  while ((m = RELATIVE.exec(text))) {
    const at = m.index;
    if (out.some((r) => at < r.end && m.index + m[0].length > r.start)) continue;
    const v1 = int(m[2]);
    out.push({ start: at, end: at + m[0].length, ref: { book: undefined, c1: undefined, v1, c2: undefined, v2: int(m[3]) ?? v1 } });
  }

  BARE.lastIndex = 0;
  while ((m = BARE.exec(text))) {
    const at = m.index;
    if (out.some((r) => at < r.end && m.index + m[0].length > r.start)) continue;
    if (namedWork(text.slice(0, at))) continue;
    const [c1, v1, a, b] = [int(m[1]), int(m[2]), int(m[3]), int(m[4])];
    const ref = b !== undefined ? { c1, v1, c2: a, v2: b } : { c1, v1, c2: c1, v2: a ?? v1 };
    out.push({ start: at, end: at + m[0].length, ref: { book: undefined, ...ref } });
  }
  return out.sort((a, b) => a.start - b.start);
}

// Give a relative reference ("vv. 3-5") the book and chapter of the passage it sits in.
export function resolveRelative(ref, context) {
  if (ref.book) return ref;
  if (!context?.book) return null;
  if (ref.c1 !== undefined) return { ...ref, book: context.book };
  if (context.c1 === undefined) return null;
  const chapter = context.c2 ?? context.c1;
  return { book: context.book, c1: chapter, v1: ref.v1, c2: chapter, v2: ref.v2 };
}

export const bookName = (osis) => DISPLAY[osis] ?? osis;

export function formatRef(ref) {
  const book = DISPLAY[ref.book] ?? ref.book;
  if (SINGLE_CHAPTER.has(ref.book) && ref.v1 !== undefined) {
    return `${book} ${ref.v1}${ref.v2 !== ref.v1 ? `\u2013${ref.v2}` : ''}`;
  }
  if (ref.v1 === undefined) return `${book} ${ref.c1}${ref.c2 !== ref.c1 ? `\u2013${ref.c2}` : ''}`;
  if (ref.c2 !== ref.c1) return `${book} ${ref.c1}:${ref.v1}\u2013${ref.c2}:${ref.v2}`;
  return `${book} ${ref.c1}:${ref.v1}${ref.v2 !== ref.v1 ? `\u2013${ref.v2}` : ''}`;
}

// A Strong's tag written beside a word: "(*aidios*, G126)" or "H539". Only numbers the lexicons
// cover, so "G20" in a sentence about a summit is left alone by the range check.
const STRONGS = /(?<![\w-])([HG])0*(\d{1,4})[a-z]?(?![\w-])/g;
const STRONGS_MAX = { H: 8674, G: 5624 };

export function findStrongs(text) {
  const out = [];
  STRONGS.lastIndex = 0;
  let m;
  while ((m = STRONGS.exec(text))) {
    const n = parseInt(m[2], 10);
    if (n < 1 || n > STRONGS_MAX[m[1]]) continue;
    out.push({ start: m.index, end: m.index + m[0].length, id: `${m[1]}${n}` });
  }
  return out;
}

export function parseStrongs(text) {
  const found = findStrongs(String(text ?? '').trim());
  return found.length ? found[0].id : null;
}

// A Greek, Hebrew or Aramaic word, with the combining accents and points it is written with.
const SCRIPT = '\\u0300-\\u036F\\u0370-\\u03FF\\u1F00-\\u1FFF\\u0590-\\u05FF\\uFB1D-\\uFB4F';
const LETTER = '\\u0386-\\u03FF\\u1F00-\\u1FFF\\u05D0-\\u05EA\\uFB1D-\\uFB4F';
const WORD = `[${SCRIPT}]*[${LETTER}][${SCRIPT}]*`;
const WORDS = new RegExp(WORD, 'gu');
const LEMMA = new RegExp(`(${WORD}(?:\\s+${WORD})*)\\s*\\([^()]*$`, 'u');
const OPENING = new RegExp(`\\((${WORD}),[^()]*$`, 'u');

// The word or phrase a study is about to gloss: text ending "ἀρραβών (*arrabōn*, " gives the span
// of ἀρραβών, and so does "the pledge (ἀρραβών, *arrabōn*, ", where the English leads and the
// Greek opens the gloss. Only an unclosed parenthesis counts, so a word glossed earlier in the
// sentence is never mistaken for the one this tag belongs to.
export function lemmaBefore(text) {
  const m = LEMMA.exec(text);
  if (m) return { start: m.index, end: m.index + m[1].length };
  const o = OPENING.exec(text);
  return o ? { start: o.index + 1, end: o.index + 1 + o[1].length } : null;
}

// A running-text ἀρραβὼν is the ἀρραβών tagged above it: Greek accents and breathings, Hebrew
// cantillation and a Greek final sigma are dropped. Hebrew vowel points are kept, because
// unpointed Hebrew merges different words.
export function wordKey(word) {
  return word
    .normalize('NFD')
    .replace(/[̀-֑ͯ-֯;·]/g, '')
    .normalize('NFC')
    .toLowerCase()
    .replace(/ς/g, 'σ');
}

export function findWords(text) {
  return [...text.matchAll(WORDS)].map((m) => ({
    start: m.index,
    end: m.index + m[0].length,
    key: wordKey(m[0]),
  }));
}
