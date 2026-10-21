// The original-language tools: what is under the English, what a word means and where it goes,
// what a translation hides, who is acting, what a verse quotes, and what the manuscripts say.
// Every answer is looked up in the data, and carries the sources it came from.

import { readRef, refLabel, splitLabel, versesOf } from './data.js';

const MAX_VERSES = 12;
const MAX_CHAPTERS_FOR_DISTINCTIONS = 3;

export const SOURCES = {
  web: 'World English Bible (public domain)',
  bsb: 'Berean Standard Bible (public domain)',
  ult: 'unfoldingWord Literal Text, with its word alignment (CC BY-SA 4.0)',
  sblgnt: 'SBL Greek New Testament (CC BY 4.0)',
  wlc: 'Westminster Leningrad Codex (public domain), Masoretic numbering',
  lxx: "Brenton's Septuagint, Greek text (public domain)",
  macula: 'MACULA Greek and Hebrew linguistic datasets, Clear Bible (CC BY 4.0)',
  stepbible: 'STEPBible lexicons TBESH/TBESG, Tyndale House (CC BY 4.0)',
  uwNotes: 'unfoldingWord Hebrew Bible and Greek NT notes (CC BY-SA 4.0)',
  dss: 'Dead Sea Scrolls biblical texts (CC BY-NC 4.0), compared at lemma level',
  openbible: 'OpenBible.info cross-references (CC BY)',
  links: "The Way's scripture links, derived from the texts (CC BY 4.0)",
  grammar: 'unfoldingWord Hebrew Grammar (CC BY-SA 4.0)',
};

const WORD = [
  'surface',
  'strongs',
  'lemma',
  'morph',
  'gloss',
  'domain',
  'class',
  'role',
  'type',
  'state',
  'subject',
  'referent',
];
const wordObject = (w) =>
  Object.fromEntries(WORD.map((k, i) => [k, w[i]]).filter(([, v]) => v != null && v !== ''));
const pointer = (list) =>
  list?.map(([surface, gloss, at]) => ({ word: surface, gloss, at: pretty(at) }));
const pretty = (label) => {
  const r = splitLabel(label);
  return r ? refLabel(r.book, r.chapter, r.verse) : label;
};

async function passage(data, input, cap = MAX_VERSES) {
  const ref = readRef(input);
  if (!ref?.book)
    throw new Error(
      `Could not read "${input}" as a Bible reference. Try "John 3:16" or "Psalm 23".`
    );
  const { verses, truncated } = await versesOf(data, ref, cap);
  if (!verses.length) throw new Error(`No verses found for "${input}".`);
  return {
    verses,
    truncated,
    note: truncated
      ? `Only the first ${cap} verses are returned; ask for a shorter passage for the rest.`
      : undefined,
  };
}

async function withLexicon(data, ids) {
  const out = {};
  await Promise.all(
    [...new Set(ids.filter(Boolean))].map(async (id) => (out[id] = await data.lexicon(id)))
  );
  return out;
}

export async function readPassage(data, { reference, include_original = true }) {
  const { verses, note } = await passage(data, reference, 40);
  return {
    reference,
    note,
    verses: verses.map(({ book, chapter, verse, data: v }) => ({
      reference: refLabel(book, chapter, verse),
      web: v.web,
      bsb: v.bsb,
      ult: v.ult,
      ...(include_original && { original: v.orig, septuagint: v.lxx }),
      ...(v.numbering && { numbered_elsewhere_as: v.numbering }),
    })),
    sources: [
      SOURCES.web,
      SOURCES.bsb,
      SOURCES.ult,
      ...(include_original ? [SOURCES.sblgnt, SOURCES.wlc, SOURCES.lxx] : []),
    ],
    quoting:
      'The WEB and BSB are public domain and may be quoted freely. Name the translation with every quotation.',
  };
}

export async function beneathTheEnglish(data, { reference }) {
  const { verses, note } = await passage(data, reference);
  const lexicon = await withLexicon(
    data,
    verses.flatMap((v) => (v.data.align ?? []).map((a) => a[2]))
  );
  return {
    reference,
    note,
    how_to_read:
      'Each English phrase of the unfoldingWord Literal Text (ULT) with the original word it renders. One English phrase can render two original words and the reverse; that is in the data, not an error.',
    verses: verses.map(({ book, chapter, verse, data: v }) => ({
      reference: refLabel(book, chapter, verse),
      ult: v.ult,
      original: v.orig,
      words: (v.align ?? []).map(([english, original, strongs, lemma]) => {
        const lex = strongs ? lexicon[strongs] : null;
        return {
          english,
          original,
          lemma,
          strongs,
          transliteration: lex?.t,
          gloss: lex?.g,
          part_of_speech: lex?.p,
        };
      }),
    })),
    sources: [SOURCES.ult, SOURCES.stepbible],
  };
}

export async function wordStudy(data, { strongs, reference, english }) {
  let id = normaliseStrongs(strongs);
  if (!id && reference && english) {
    const { verses } = await passage(data, reference, 3);
    const want = english.toLowerCase();
    const hit = verses
      .flatMap((v) => v.data.align ?? [])
      .find(([e]) => e.toLowerCase().includes(want));
    id = hit?.[2] ?? null;
    if (!id)
      throw new Error(
        `No word rendered "${english}" in ${reference}. Call beneath_the_english to see the words there.`
      );
  }
  if (!id)
    throw new Error(
      'Give a Strong\'s number ("G25", "H2617"), or a reference and the English word to look up.'
    );
  const [lex, usage, studies] = await Promise.all([
    data.lexicon(id),
    data.usage(id),
    data.studiesByPassage(),
  ]);
  if (!lex && !usage) throw new Error(`No entry for ${id}.`);
  const occurrences = usage?.occurrences ?? [];
  const byBook = {};
  for (const label of occurrences) {
    const r = splitLabel(label);
    if (r) byBook[r.book] = (byBook[r.book] ?? 0) + 1;
  }
  const discussing = (studies?.words?.[id] ?? []).map((i) => studies.studies[i]).filter(Boolean);
  return {
    strongs: id,
    lemma: lex?.l,
    transliteration: lex?.t,
    language: lex?.lang,
    part_of_speech: lex?.p,
    gloss: lex?.g,
    counts: lex?.c,
    verses_in_the_hebrew_or_greek_text: occurrences.length,
    books: Object.entries(byBook)
      .sort((a, b) => b[1] - a[1])
      .map(([book, n]) => ({ book: refLabel(book, '').trim(), verses: n })),
    occurrences:
      occurrences.length <= 60
        ? occurrences.map(pretty)
        : { first_60: occurrences.slice(0, 60).map(pretty), total: occurrences.length },
    renderings_in_the_ult: (usage?.renderings ?? []).map(([english, n]) => ({ english, times: n })),
    studies_on_this_site_that_discuss_it: discussing.map((s) => ({
      title: s.t,
      url: `https://the-way.lewy.au/${s.u}`,
    })),
    caution:
      'A gloss is a starting point. What a word means in a passage is decided by how it is used there and elsewhere, never by its root or etymology alone.',
    sources: [SOURCES.stepbible, SOURCES.macula, SOURCES.ult],
  };
}

// The innovation: where English hides what the original shows. Two different original words
// rendered by the same English word (agapao/phileo, "love", in John 21:15-17), or one original
// word rendered several ways, inside the passage the reader is studying.
export async function hiddenDistinctions(data, { reference }) {
  const ref = readRef(reference);
  if (!ref?.book) throw new Error(`Could not read "${reference}" as a Bible reference.`);
  if (ref.c2 - ref.c1 >= MAX_CHAPTERS_FOR_DISTINCTIONS)
    throw new Error('Ask for three chapters or fewer.');
  const { verses } = await versesOf(data, ref, 400);
  const lexicon = await withLexicon(
    data,
    verses.flatMap((v) => (v.data.align ?? []).map((a) => a[2]))
  );
  const byEnglish = new Map();
  const byWord = new Map();
  for (const { book, chapter, verse, data: v } of verses) {
    const at = refLabel(book, chapter, verse);
    for (const [english, original, strongs, lemma] of v.align ?? []) {
      if (!strongs || !CONTENT_POS.has(lexicon[strongs]?.p)) continue;
      for (const token of contentWords(english)) {
        const entry = byEnglish.get(token) ?? new Map();
        const forWord = entry.get(strongs) ?? { lemma, original, at: [] };
        if (!forWord.at.includes(at)) forWord.at.push(at);
        entry.set(strongs, forWord);
        byEnglish.set(token, entry);
      }
      const renderings = byWord.get(strongs) ?? { lemma, as: new Map() };
      const key = english.toLowerCase();
      renderings.as.set(key, [...(renderings.as.get(key) ?? []), at]);
      byWord.set(strongs, renderings);
    }
  }
  const describe = (id, w) => ({
    strongs: id,
    lemma: w.lemma,
    transliteration: lexicon[id]?.t,
    gloss: lexicon[id]?.g,
    verses: w.at,
  });
  const oneEnglishSeveralWords = [...byEnglish.entries()]
    .filter(([, words]) => words.size > 1)
    .map(([english, words]) => ({
      english,
      original_words: [...words.entries()].map(([id, w]) => describe(id, w)),
    }));
  const oneWordSeveralEnglish = [...byWord.entries()]
    .filter(([, w]) => w.as.size > 2)
    .map(([id, w]) => ({
      strongs: id,
      lemma: w.lemma,
      transliteration: lexicon[id]?.t,
      gloss: lexicon[id]?.g,
      rendered_as: [...w.as.entries()].map(([english, at]) => ({ english, verses: at })),
    }));
  return {
    reference,
    what_this_shows:
      'Places in this passage where English hides what the original shows: one English word standing for different Hebrew or Greek words, and one original word translated several ways. Each is a question to investigate, not a conclusion; a different word can be stylistic variation, so read the context before resting anything on it.',
    one_english_word_for_several_original_words: oneEnglishSeveralWords,
    one_original_word_translated_several_ways: oneWordSeveralEnglish,
    sources: [SOURCES.ult, SOURCES.stepbible],
  };
}

const STOP = new Set(
  'a an the and or but of to in on at by for with from into upon unto as is was be been are were it its he she they them his her their him you your yours we us our i me my mine this that these those there then so not no do did does have has had will shall would should may might can could who whom which what when where why how all any each every some one also even very up out about over under than'.split(
    ' '
  )
);
// Content words only. Articles, conjunctions, particles, prepositions and pronouns are rendered
// every which way by any translation, so a "distinction" among them is noise. A positive list,
// because the lexicon's part-of-speech codes for function words are irregular ('t', 'prt', 'd').
const CONTENT_POS = new Set(['noun', 'verb', 'name', 'adjective', 'adverb', 'adv']);

function contentWords(english) {
  return english
    .toLowerCase()
    .replace(/[^a-z' ]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOP.has(w));
}

export async function whoIsActing(data, { reference }) {
  const { verses, note } = await passage(data, reference, 6);
  return {
    reference,
    note,
    how_to_read:
      'MACULA annotates who does what: each verb with its subject, including subjects carried only by the verb ending, and each pronoun with the word it points back to. Coverage is partial: a missing role means "not annotated", never "no subject".',
    verses: verses.map(({ book, chapter, verse, data: v }) => ({
      reference: refLabel(book, chapter, verse),
      original: v.orig,
      web: v.web,
      words: (v.words ?? [])
        .map(wordObject)
        .filter((w) => w.subject || w.referent || w.role)
        .map((w) => ({
          word: w.surface,
          lemma: w.lemma,
          gloss: w.gloss,
          strongs: w.strongs,
          role: ROLE[w.role] ?? w.role,
          verb_form: w.type,
          subject: pointer(w.subject),
          refers_to: pointer(w.referent),
        })),
    })),
    sources: [SOURCES.macula],
  };
}

const ROLE = {
  s: 'subject',
  v: 'verb',
  o: 'object',
  io: 'indirect object',
  adv: 'adverbial',
  p: 'predicate',
  vc: 'copula',
};

export async function originalWords(data, { reference }) {
  const { verses, note } = await passage(data, reference, 6);
  const lexicon = await withLexicon(
    data,
    verses.flatMap((v) => (v.data.words ?? []).map((w) => w[1]))
  );
  return {
    reference,
    note,
    verses: verses.map(({ book, chapter, verse, data: v }) => ({
      reference: refLabel(book, chapter, verse),
      original: v.orig,
      words: (v.words ?? []).map((w) => {
        const o = wordObject(w);
        delete o.subject;
        delete o.referent;
        return {
          ...o,
          transliteration: lexicon[o.strongs]?.t,
          lexicon_gloss: lexicon[o.strongs]?.g,
        };
      }),
    })),
    domain_codes:
      'Greek domains are Louw-Nida numbers (25.43 is "love, affection"); Hebrew domains are SDBH codes.',
    sources: [SOURCES.macula, SOURCES.stepbible],
  };
}

export async function quotationTrace(data, { reference }) {
  const { verses, note } = await passage(data, reference, 6);
  return {
    reference,
    note,
    how_to_read:
      'Links found in the texts themselves, grouped by how they were found. quotation-greek (the New Testament quoting the Septuagint word for word) and inner-biblical (the Old Testament quoting itself in Hebrew) are textual facts. allusion-lemma is shared rare vocabulary. quotation-hebrew is a 19th-century translator\'s judgement, to verify in Greek. "shared" is the longest run of words the two verses actually share. No link found means the method found none, not that there is no connection: a paraphrase leaves no shared words.',
    verses: verses.map(({ book, chapter, verse, data: v }) => ({
      reference: refLabel(book, chapter, verse),
      original: v.orig,
      links: (v.links ?? []).map((l) => ({
        ...l,
        reference: l.reference && pretty(l.reference),
        english_reference: l.english_reference && pretty(l.english_reference),
      })),
    })),
    sources: [SOURCES.links, SOURCES.sblgnt, SOURCES.lxx, SOURCES.wlc, SOURCES.dss],
  };
}

export async function textualNotes(data, { reference }) {
  const { verses, note } = await passage(data, reference);
  return {
    reference,
    note,
    how_to_read:
      "Qere: the Masoretes' marginal reading beside the written text (Ketiv). Translator notes: the unfoldingWord translators' record of a decision. Scroll readings: a word a Dead Sea Scroll has that the Masoretic text lacks, with how many words of that verse survive in the scroll; weigh a reading by how much of the verse is legible.",
    verses: verses
      .map(({ book, chapter, verse, data: v }) => ({
        reference: refLabel(book, chapter, verse),
        numbered_elsewhere_as: v.numbering,
        notes: (v.notes ?? []).map(([work, type, text]) => ({ source: work, type, text })),
        scroll_readings: (v.scrolls ?? []).map(([scroll, lemma, extant]) => ({
          scroll,
          lemma,
          words_of_the_verse_surviving: extant,
        })),
      }))
      .filter((v) => v.numbered_elsewhere_as || v.notes.length || v.scroll_readings.length),
    sources: [SOURCES.uwNotes, SOURCES.dss],
  };
}

export async function crossReferences(data, { reference }) {
  const ref = readRef(reference);
  if (!ref?.book || ref.v1 === undefined) throw new Error('Give one verse, e.g. "Romans 8:28".');
  const book = await data.webBook(ref.book);
  const list = book?.x?.[`${ref.c1}:${ref.v1}`] ?? [];
  return {
    reference: refLabel(ref.book, ref.c1, ref.v1),
    text: book?.v?.[ref.c1]?.[ref.v1],
    cross_references: await Promise.all(
      list.map(async ([b, c, v, end]) => ({
        reference: refLabel(b, c, v) + (end ? `-${end}` : ''),
        web: (await data.webBook(b))?.v?.[c]?.[v],
      }))
    ),
    note: 'The strongest OpenBible.info cross-references by reader votes: leads to follow, not evidence. quotation_trace gives the links found in the texts themselves.',
    sources: [SOURCES.openbible, SOURCES.web],
  };
}

export async function hebrewGrammar(data, { topic }) {
  const articles = (await data.grammar()) ?? [];
  const terms = String(topic ?? '')
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);
  const scored = articles
    .map((a) => {
      const title = a.title.toLowerCase();
      const body = a.body.toLowerCase();
      const score = terms.reduce(
        (s, t) => s + (title.includes(t) ? 5 : 0) + (body.includes(t) ? 1 : 0),
        0
      );
      return { a, score };
    })
    .filter((x) => x.score > 0)
    .sort((x, y) => y.score - x.score);
  if (!scored.length) return { topic, matches: [], available: articles.map((a) => a.title) };
  return {
    topic,
    article: { title: scored[0].a.title, text: scored[0].a.body },
    other_matches: scored.slice(1, 6).map((x) => x.a.title),
    sources: [SOURCES.grammar],
  };
}

export function normaliseStrongs(input) {
  const m = /^\s*([HGhg])\s*0*(\d{1,4})[a-z]?\s*$/.exec(String(input ?? ''));
  return m ? `${m[1].toUpperCase()}${parseInt(m[2], 10)}` : null;
}
