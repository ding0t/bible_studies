// Where the connector's data comes from. Everything is a static file the site already serves:
// the original-language shards (references/build/export_connector.py, assets/lang/), the pop-up
// verse and lexicon files (export_popups.py, assets/popups/), the study index and markdown copies
// (hooks/llms.py), and the page-scan study index (hooks/popups.py). The Worker reads them through
// its ASSETS binding and the tests read them from a built site directory, so one loader function
// is all that differs.

import { BOOK_ORDER, bookName, parseRef } from '../utils/scriptureRefs.js';

export function createData(fetchText) {
  const cache = new Map();

  async function json(path) {
    if (!cache.has(path)) {
      cache.set(
        path,
        fetchText(path).then((text) => (text == null ? null : JSON.parse(text)))
      );
    }
    return cache.get(path);
  }

  return {
    text: (path) => fetchText(path),
    json,
    chapter: (book, chapter) => json(`assets/lang/chapters/${book}/${chapter}.json`),
    lexicon: (id) =>
      json(`assets/popups/words/${bucket(id)}.json`).then((d) => d?.[id.slice(1)] ?? null),
    usage: (id) =>
      json(`assets/lang/words/${bucket(id)}.json`).then((d) => d?.[id.slice(1)] ?? null),
    // The site's reading translation, as export_popups.py wrote it; `t` names which.
    readingBook: (book) => json(`assets/popups/verses/${book}.json`),
    studiesIndex: () => json('assets/studies-index.json'),
    studiesByPassage: () => json('assets/popups/studies.json'),
    grammar: () => json('assets/lang/grammar.json'),
    searchSections: () => json('assets/search/sections.json'),
    searchTerms: (prefix) => json(`assets/search/terms/${prefix}.json`),
  };
}

function bucket(id) {
  return `${id[0]}${String(Math.floor(parseInt(id.slice(1), 10) / 100)).padStart(2, '0')}`;
}

// A reference as a user or an AI types it: "john 3:16", "1 cor 13", "Ps. 23:1-3". The site's parser
// wants a capitalised book name (in prose "job 3" is a noun), so capitalise before parsing.
export function readRef(input) {
  if (!input) return null;
  const text = String(input)
    .trim()
    .replace(/\b([a-z])/g, (c) => c.toUpperCase());
  const ref = parseRef(text);
  if (!ref) return null;
  return ref;
}

export function refLabel(book, chapter, verse) {
  return `${bookName(book)} ${chapter}${verse != null ? `:${verse}` : ''}`;
}

// Every [book, chapter, verse] a reference covers, capped so one call cannot ask for a whole book.
export async function versesOf(data, ref, cap) {
  const out = [];
  for (let c = ref.c1; c <= ref.c2; c++) {
    const chapter = await data.chapter(ref.book, c);
    if (!chapter) continue;
    const numbers = Object.keys(chapter.verses)
      .map(Number)
      .sort((a, b) => a - b);
    for (const v of numbers) {
      if (ref.v1 !== undefined && c === ref.c1 && v < ref.v1) continue;
      if (ref.v2 !== undefined && c === ref.c2 && v > ref.v2) continue;
      out.push({ book: ref.book, chapter: c, verse: v, data: chapter.verses[v], ot: chapter.ot });
      if (out.length >= cap) return { verses: out, truncated: true };
    }
  }
  return { verses: out, truncated: false };
}

// "John 21:15" -> {book, chapter, verse}, for references stored as labels in the data files.
export function splitLabel(label) {
  const ref = readRef(label);
  return ref ? { book: ref.book, chapter: ref.c1, verse: ref.v1 } : null;
}

export const BOOKS = BOOK_ORDER;
