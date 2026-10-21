// The study tools: find a study by question or topic, find the studies on a passage, read one.

import { BOOK_ORDER } from '../utils/scriptureRefs.js';
import { readRef, refLabel } from './data.js';

export const SITE = 'https://the-way.lewy.au/';
const STOP = new Set(
  'a an the and or of to in on is are was be do does did i my me can how what why who when where which about with for it its this that you your'.split(
    ' '
  )
);

function terms(text) {
  return String(text ?? '')
    .toLowerCase()
    .replace(/[^a-z0-9' ]/g, ' ')
    .split(/\s+/)
    .filter((t) => t.length > 1 && !STOP.has(t));
}

function stem(t) {
  return t.replace(/(ing|ed|es|s)$/, '');
}

export async function searchStudies(data, { query, limit = 6 }) {
  const index = (await data.studiesIndex()) ?? [];
  const wanted = terms(query).map(stem);
  if (!wanted.length) throw new Error('Give a question or topic to search for.');
  const scored = index
    .map((s) => {
      const fields = [
        [s.questions.join(' '), 4],
        [s.title, 3],
        [s.tags.join(' '), 2],
        [s.summary, 1],
      ];
      let score = 0;
      for (const w of wanted) {
        for (const [text, weight] of fields) {
          if (terms(text).some((t) => stem(t) === w)) score += weight;
        }
      }
      const q = String(query)
        .toLowerCase()
        .trim()
        .replace(/[?.!]+$/, '');
      if (s.questions.some((x) => x.toLowerCase().replace(/[?.!]+$/, '') === q)) score += 50;
      return { s, score };
    })
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, Math.min(limit, 15));
  return {
    query,
    results: scored.map(({ s }) => ({
      title: s.title,
      url: SITE + s.url,
      markdown: `${SITE}${s.url}index.md`,
      in_one_sentence: s.summary,
      passage: s.passage || undefined,
      answers: s.questions.length ? s.questions : undefined,
    })),
    next: 'Read a study with get_study. Quote its one-sentence thesis rather than summarising it afresh, and point the reader to the verses it rests on.',
  };
}

export async function studiesForPassage(data, { reference }) {
  const ref = readRef(reference);
  if (!ref?.book) throw new Error(`Could not read "${reference}" as a Bible reference.`);
  const { studies = [], commentary = {} } = (await data.studiesByPassage()) ?? {};
  const hits = { primary: [], cites: [] };
  for (const s of studies) {
    const overlaps = (list) => list.some((r) => overlap(readRef(r), ref));
    if (overlaps(s.p)) hits.primary.push(s);
    else if (overlaps(s.r)) hits.cites.push(s);
  }
  const bookNumber = String(BOOK_INDEX(ref.book));
  const chapterPage = commentary[bookNumber]?.[String(ref.c1)];
  const shape = (s) => ({
    title: s.t,
    url: SITE + s.u,
    primary_passage: s.p.join('; ') || undefined,
  });
  return {
    reference: refLabel(ref.book, ref.c1, ref.v1),
    studies_about_this_passage: hits.primary.map(shape),
    studies_that_cite_it: hits.cites.slice(0, 25).map(shape),
    more:
      hits.cites.length > 25
        ? `${hits.cites.length - 25} more cite it; see the chapter page.`
        : undefined,
    chapter_page: chapterPage ? SITE + chapterPage : undefined,
  };
}

function overlap(a, b) {
  if (!a?.book || a.book !== b.book) return false;
  const start = (r) => r.c1 * 1000 + (r.v1 ?? 0);
  const end = (r) => r.c2 * 1000 + (r.v2 ?? 999);
  return start(a) <= end(b) && start(b) <= end(a);
}

const BOOK_INDEX = (book) => BOOK_ORDER.indexOf(book) + 1;

export async function getStudy(data, { url, section }) {
  const path = studyPath(url);
  if (!path)
    throw new Error(
      'Give a study URL from search_studies, e.g. https://the-way.lewy.au/salvation/assurance-of-salvation/'
    );
  const text = await data.text(`${path}index.md`);
  if (text == null) throw new Error(`No page at ${SITE}${path}.`);
  const body = text.replace(/^---\n[\s\S]*?\n---\n/, '');
  const headings = [...body.matchAll(/^(#{2,3}) (.+)$/gm)].map((m) => m[2]);
  if (!section) {
    return {
      url: SITE + path,
      sections: headings,
      markdown:
        body.length > 60000
          ? body.slice(0, 60000) + '\n\n[Truncated: ask for one section by name.]'
          : body,
      credit: `Quote with a link to ${SITE}${path}. The site's own writing is CC BY 4.0; quoted Bible translations keep their own terms.`,
    };
  }
  const want = section.toLowerCase();
  const lines = body.split('\n');
  const start = lines.findIndex((l) => /^#{2,3} /.test(l) && l.toLowerCase().includes(want));
  if (start < 0)
    return { url: SITE + path, error: `No section matching "${section}".`, sections: headings };
  const level = lines[start].match(/^#+/)[0].length;
  let end = lines.findIndex((l, i) => i > start && new RegExp(`^#{1,${level}} `).test(l));
  if (end < 0) end = lines.length;
  return {
    url: SITE + path,
    section: lines[start].replace(/^#+ /, ''),
    markdown: lines.slice(start, end).join('\n'),
  };
}

function studyPath(url) {
  if (!url) return null;
  let path = String(url)
    .trim()
    .replace(/^https?:\/\/[^/]+\//, '')
    .replace(/^\//, '');
  path = path.replace(/index\.(md|html)$/, '').replace(/\.md$/, '/');
  if (path && !path.endsWith('/')) path += '/';
  if (path.includes('..')) return null;
  return path;
}
