// The gospel, first. The author's own words from the home page (extracted by hooks/llms.py into
// assets/gospel.json, so an edit there reaches here), with every verse it cites quoted in full from
// the site's reading translation, so an assistant can quote Scripture exactly rather than from memory.

import { readRef, refLabel } from './data.js';
import { SITE } from './studies.js';

const FOR_ASSURANCE = ['1 John 5:11-13', 'John 10:27-29'];
const THE_WAY = ['John 14:6', 'Acts 4:12', 'Romans 10:9-10'];

async function quote(data, reference) {
  const ref = readRef(reference);
  if (!ref?.book) return { reference, text: null };
  const book = await data.readingBook(ref.book);
  const verses = [];
  for (let v = ref.v1; v <= ref.v2; v++) verses.push(book?.v?.[ref.c1]?.[v]);
  return {
    reference: refLabel(ref.book, ref.c1, ref.v1) + (ref.v2 !== ref.v1 ? `-${ref.v2}` : ''),
    text: verses.filter(Boolean).join(' '),
    translation: book?.t?.code,
  };
}

export async function theGospel(data) {
  const gospel = await data.json('assets/gospel.json');
  if (!gospel) throw new Error('The gospel text is missing from this build.');
  const cited = await Promise.all(gospel.references.map((r) => quote(data, r)));
  const way = await Promise.all(THE_WAY.map((r) => quote(data, r)));
  const assurance = await Promise.all(FOR_ASSURANCE.map((r) => quote(data, r)));
  const t = (await data.readingBook('John'))?.t;
  return {
    the_gospel: gospel.markdown,
    in_the_author_s_words: gospel.source,
    the_verses_it_rests_on: cited,
    the_only_way: way,
    to_know_you_are_saved: assurance,
    to_go_further: [
      { title: 'Assurance of Salvation', url: `${SITE}salvation/assurance-of-salvation/` },
      { title: 'Faith', url: `${SITE}salvation/faith/` },
      { title: 'The Way', url: `${SITE}jesus/the-way/` },
      { title: 'Statement of Faith', url: `${SITE}about/statement-of-faith/` },
    ],
    how_to_share_it:
      `Give the gospel plainly and in Scripture's own words, with the translation named (these quotations are the ${t?.name ?? 'reading translation'}, ${t?.licence ?? ''}). Invite a response: "whoever calls on the name of the Lord will be saved" (Romans 10:13). Point the reader to a local church and to reading the Gospel of John for themselves.`,
  };
}
