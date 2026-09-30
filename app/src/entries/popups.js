// Verse and word pop-ups on every page. Loaded site-wide through mkdocs.yml extra_javascript.
//
// A reader meets a reference ("Romans 8:28", "vv. 3-5") or a Strong's tag ("G126") and can read
// the verse or the word without leaving the study. Nothing in the markdown changes: the script
// finds references in the rendered text. Two explicit markers cover what the text alone cannot
// say -- <span data-ref="Gen 7:11">7:11</span> and <span data-strongs="H7657">Seventy</span>.
//
// Data: assets/popups/verses/<Book>.json and words/<H|G><nn>.json are exported from bible-text.db
// by references/build/export_popups.py (committed); assets/popups/studies.json is written at
// build time by hooks/popups.py from page frontmatter.
import {
  BOOK_ORDER,
  bookName,
  findBookNames,
  findRefs,
  findStrongs,
  findWords,
  formatRef,
  lemmaBefore,
  namedWork,
  parseRef,
  parseStrongs,
  resolveRelative,
} from '../utils/scriptureRefs.js';

const SITE = new URL('../../', import.meta.url);
const DATA = new URL('assets/popups/', SITE);
const MAX_VERSES = 40;
const CONTEXT = 3;
const MAX_STUDIES = 6;
const HOVER_OPEN_MS = 350;
const HOVER_CLOSE_MS = 250;

// Text inside these is never scanned: links already go somewhere, headings are navigation, and
// code, diagrams and the React tools own their own text.
const SKIP = [
  'a', 'code', 'pre', 'kbd', 'script', 'style', 'button', 'textarea', 'svg', 'h1', 'h2', 'h3', 'h4',
  'h5', 'h6', '.mermaid', '.headerlink', '.pop-ref', '.pop-word', '[data-no-popups]', '[id$="-root"]',
].join(',');
const BLOCK = 'p, li, td, th, dd, blockquote, figcaption';
const HEADING = /^H([2-6])$/;

const cache = new Map();
function load(path) {
  if (!cache.has(path)) {
    cache.set(
      path,
      fetch(new URL(path, DATA)).then((r) => {
        if (!r.ok) throw new Error(`${path}: ${r.status}`);
        return r.json();
      })
    );
  }
  return cache.get(path);
}

const refs = new WeakMap();

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === 'class') node.className = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? '' : v);
  }
  for (const child of children.flat()) {
    if (child !== undefined && child !== null && child !== false) node.append(child);
  }
  return node;
}

function trigger(kind, value, text) {
  const node = el('span', { class: kind === 'ref' ? 'pop-ref' : 'pop-word', role: 'button', tabindex: '0' }, text);
  refs.set(node, { kind, value });
  if (kind === 'ref') node.setAttribute('aria-label', `${text.trim()}: show ${formatRef(value)}`);
  else node.setAttribute('aria-label', `${text.trim()}: show word study ${value}`);
  return node;
}

// ---------------------------------------------------------------------------------------------
// Finding references in the page

function scan(root) {
  const tagged = new Map();
  for (const node of root.querySelectorAll('[data-ref]')) {
    const ref = parseRef(node.dataset.ref);
    if (ref) adopt(node, 'ref', ref);
  }
  for (const node of root.querySelectorAll('[data-strongs]')) {
    const id = parseStrongs(node.dataset.strongs);
    if (id) claim(node, id, tagged);
  }

  // Walk elements and text together, in reading order, so a relative "v. 20" or a bare "5:1" can be
  // resolved against the passage the reader is in: the last reference or book named in words in the
  // same paragraph, else the quotation's own reference line, else the section heading's, else the
  // page's primary_passage (put on the page by hooks/popups.py).
  const page = parseRef(root.querySelector('[data-primary-passage]')?.dataset.primaryPassage);
  const headings = [];
  const lastInBlock = new WeakMap();
  const blockText = new WeakMap();
  const texts = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        const level = HEADING.exec(node.tagName);
        if (level) {
          const found = findRefs(node.textContent).find((r) => r.ref.book);
          while (headings.length && headings[headings.length - 1].level >= +level[1]) headings.pop();
          if (found) headings.push({ level: +level[1], ref: found.ref });
          return NodeFilter.FILTER_REJECT;
        }
        return node.matches(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP;
      }
      return NodeFilter.FILTER_ACCEPT;
    },
  });
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const block = node.parentElement.closest(BLOCK);
    const quote = node.parentElement.closest('blockquote');
    const before = (block && blockText.get(block)) || '';
    if (block) blockText.set(block, before + node.data);
    const matches = [];
    const found = [
      ...findRefs(node.data),
      ...findBookNames(node.data).map(({ start, book }) => ({ start, named: { book } })),
    ].sort((a, b) => a.start - b.start);
    for (const { start, end, ref, named } of found) {
      if (named) {
        if (block) lastInBlock.set(block, named);
        continue;
      }
      let resolved = ref;
      if (!ref.book) {
        if (ref.c1 !== undefined && namedWork(before + node.data.slice(0, start))) continue;
        // A numbered reference in the same paragraph or cell comes first; a book only named in words
        // there yields to a table's column header, which names the book for the whole column.
        const nearest = block && lastInBlock.get(block);
        const contexts = [
          nearest?.c1 !== undefined ? nearest : null,
          columnBook(node),
          nearest,
          quote && lastInBlock.get(quote),
          headings[headings.length - 1]?.ref,
          page,
        ];
        resolved = null;
        for (const context of contexts) if (!resolved && context) resolved = resolveRelative(ref, context);
        if (!resolved) continue;
      } else {
        if (block) lastInBlock.set(block, ref);
        if (quote && !lastInBlock.has(quote)) lastInBlock.set(quote, ref);
      }
      matches.push({ start, end, kind: 'ref', value: resolved });
    }
    for (const { start, end, id } of findStrongs(node.data)) {
      if (!matches.some((m) => start < m.end && end > m.start)) matches.push({ start, end, kind: 'word', value: id });
    }
    if (matches.length) texts.push({ node, matches: matches.sort((a, b) => a.start - b.start) });
  }

  for (const { node, matches } of texts) {
    const fragment = document.createDocumentFragment();
    const words = [];
    let at = 0;
    for (const m of matches) {
      const made = trigger(m.kind, m.value, node.data.slice(m.start, m.end));
      fragment.append(node.data.slice(at, m.start), made);
      if (m.kind === 'word') words.push(made);
      at = m.end;
    }
    fragment.append(node.data.slice(at));
    node.replaceWith(fragment);
    for (const made of words) linkWord(made, refs.get(made).value, tagged);
  }
  linkRepeats(root, tagged);
}

// Studies write a word as <span dir="rtl">גֹּאֵל</span> (*goel*, H1350), **ἀΐδιος** (*aidios*,
// G126) or plain ἀρραβών (*arrabōn*, G728). The number is the reliable hook, but the reader
// reaches for the word, so the word in front of the parenthesis opens the same card.
const ORIGINAL = /[Ͱ-Ͽἀ-῿֐-׿]/;
function linkWord(tag, id, tagged) {
  let between = '';
  for (let node = tag.previousSibling; node; node = node.previousSibling) {
    if (node.nodeType === Node.ELEMENT_NODE && ORIGINAL.test(node.textContent) && !refs.has(node)) {
      // **ἀρραβών** (… before the gloss, or (**ἀρραβών**, … opening it.
      const opens = /\($/.test(node.previousSibling?.textContent ?? '') && /^,[^()]*$/.test(between);
      if (/^\s*\([^()]*$/.test(between) || opens) claim(node, id, tagged);
      return;
    }
    if (node.nodeType === Node.TEXT_NODE && node.data.includes('(')) {
      const found = lemmaBefore(node.data + between);
      if (found) {
        if (found.end <= node.data.length) {
          const word = node.splitText(found.start);
          word.splitText(found.end - found.start);
          const wrapped = el('span', {}, word.data);
          word.replaceWith(wrapped);
          claim(wrapped, id, tagged);
        }
        return;
      }
      // Only " (" between the tag and an element: the word is the <span dir="rtl"> or <strong>.
      if (node.data.slice(0, node.data.lastIndexOf('(')).trim()) return;
    }
    between = node.textContent + between;
    if (between.length > 80 || between.includes(')')) return;
  }
}

// A word the page has tagged once is the same word when it comes back: ἀρραβών glossed with G728
// in one section opens G728 wherever else the study names it. A form the page tags with two
// different numbers is left alone.
function claim(node, id, tagged) {
  adopt(node, 'word', id);
  const words = findWords(node.textContent);
  if (words.length !== 1) return;
  const { key } = words[0];
  tagged.set(key, tagged.has(key) && tagged.get(key) !== id ? null : id);
}

function linkRepeats(root, tagged) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        return node.matches(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP;
      }
      return ORIGINAL.test(node.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
    },
  });
  const found = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const words = findWords(node.data).filter((w) => tagged.get(w.key));
    if (words.length) found.push({ node, words });
  }
  for (const { node, words } of found) {
    const fragment = document.createDocumentFragment();
    let at = 0;
    for (const w of words) {
      fragment.append(node.data.slice(at, w.start), trigger('word', tagged.get(w.key), node.data.slice(w.start, w.end)));
      at = w.end;
    }
    fragment.append(node.data.slice(at));
    node.replaceWith(fragment);
  }
}

// A table whose column header names the book -- "| Day | Genesis |" over rows of "(1:3-5)".
function columnBook(node) {
  const cell = node.parentElement.closest('td');
  const header = cell?.closest('table')?.querySelectorAll('thead th')[cell.cellIndex];
  if (!header) return null;
  const ref = findRefs(header.textContent).find((r) => r.ref.book);
  const named = findBookNames(header.textContent)[0];
  return ref ? ref.ref : named ? { book: named.book } : null;
}

function adopt(node, kind, value) {
  node.classList.add(kind === 'ref' ? 'pop-ref' : 'pop-word');
  node.setAttribute('role', 'button');
  node.setAttribute('tabindex', '0');
  refs.set(node, { kind, value });
}

// ---------------------------------------------------------------------------------------------
// The card

const card = el('div', { class: 'pop-card', role: 'dialog', 'aria-live': 'polite', hidden: true });
const back = el('button', { type: 'button', class: 'pop-back', 'aria-label': 'Back', title: 'Back' }, '←');
const title = el('span', { class: 'pop-title' });
const close = el('button', { type: 'button', class: 'pop-close', 'aria-label': 'Close', title: 'Close' }, '×');
const body = el('div', { class: 'pop-body' });
card.append(el('div', { class: 'pop-head' }, back, title, close), body);

let anchor = null;
let pinned = false;
let history = [];
let openTimer = null;
let closeTimer = null;

function show(item, from, pin) {
  anchor = from;
  pinned = pin;
  history = [item];
  render();
  card.hidden = false;
  place();
}

function hide() {
  card.hidden = true;
  const returnTo = pinned ? anchor : null;
  anchor = null;
  pinned = false;
  if (returnTo && card.contains(document.activeElement)) returnTo.focus();
}

function navigate(item) {
  pinned = true;
  history.push(item);
  render();
}

function place() {
  if (!anchor || card.hidden) return;
  if (window.matchMedia('(max-width: 600px)').matches) {
    card.classList.add('pop-sheet');
    card.style.left = card.style.top = '';
    return;
  }
  card.classList.remove('pop-sheet');
  card.style.maxHeight = '';
  const rect = anchor.getClientRects()[0] ?? anchor.getBoundingClientRect();
  const width = card.offsetWidth;
  const height = card.offsetHeight;
  const left = Math.max(8, Math.min(rect.left, window.innerWidth - width - 8));
  // Below if it fits, above if only that fits, else whichever side is roomier, scrolling inside.
  const below = window.innerHeight - rect.bottom - 14;
  const above = rect.top - 14 - (document.querySelector('.md-header')?.offsetHeight ?? 0);
  const goAbove = height > below && (height <= above || above > below);
  if (height > (goAbove ? above : below)) card.style.maxHeight = `${goAbove ? above : below}px`;
  const top = goAbove ? rect.top - Math.min(height, above) - 6 : rect.bottom + 6;
  card.style.left = `${left + window.scrollX}px`;
  card.style.top = `${top + window.scrollY}px`;
}

async function render() {
  const item = history[history.length - 1];
  back.hidden = history.length < 2;
  body.replaceChildren(el('p', { class: 'pop-muted' }, 'Loading…'));
  try {
    if (item.kind === 'ref') await renderVerse(item.value, item.context);
    else await renderWord(item.value);
  } catch {
    body.replaceChildren(el('p', { class: 'pop-muted' }, 'This could not be loaded. The reference is left as written.'));
  }
  place();
}

// ---------------------------------------------------------------------------------------------
// Verses

const key = (c, v) => c * 1000 + v;

function span(ref) {
  const from = key(ref.c1, ref.v1 ?? 0);
  const to = key(ref.c2, ref.v2 ?? 999);
  return [from, to];
}

async function renderVerse(ref, withContext = false) {
  title.textContent = formatRef(ref);
  card.setAttribute('aria-label', formatRef(ref));
  const book = await load(`verses/${ref.book}.json`);
  const [from, to] = span(ref);
  const lastChapter = Math.max(...Object.keys(book.v).map(Number));

  const verses = [];
  for (let c = ref.c1; c <= Math.min(ref.c2, lastChapter); c++) {
    const chapter = book.v[c] ?? {};
    for (const v of Object.keys(chapter).map(Number).sort((a, b) => a - b)) {
      const k = key(c, v);
      const near = withContext && ref.v1 !== undefined && k >= from - CONTEXT && k <= to + CONTEXT && c >= ref.c1 && c <= ref.c2;
      if ((k >= from && k <= to) || near) verses.push({ c, v, text: chapter[v], cited: k >= from && k <= to });
    }
  }
  // Context reaching into the neighbouring chapter is not worth the complexity; stay in-chapter.
  if (!verses.length) {
    body.replaceChildren(el('p', { class: 'pop-muted' }, `${formatRef(ref)} is not in the World English Bible's numbering.`));
    return;
  }

  const shown = verses.slice(0, MAX_VERSES);
  const multiChapter = ref.c2 !== ref.c1;
  const text = el('div', { class: 'pop-text' });
  let chapterShown = null;
  for (const { c, v, text: words, cited } of shown) {
    if (multiChapter && c !== chapterShown) {
      text.append(el('span', { class: 'pop-chapter' }, `Chapter ${c}`));
      chapterShown = c;
    }
    text.append(el('span', { class: cited ? 'pop-verse' : 'pop-verse pop-around' }, el('sup', {}, String(v)), ' ', words, ' '));
  }

  const actions = el('div', { class: 'pop-actions' });
  if (ref.v1 !== undefined) {
    actions.append(
      el('button', {
        type: 'button',
        class: 'pop-link',
        onclick: () => {
          history[history.length - 1] = { kind: 'ref', value: ref, context: !withContext };
          pinned = true;
          render();
        },
      }, withContext ? 'Hide context' : 'Show context')
    );
  }
  const chapterUrl = await commentaryUrl(ref);
  if (chapterUrl) actions.append(el('a', { class: 'pop-link', href: chapterUrl }, `${formatRef({ ...ref, v1: undefined, c2: ref.c1 })} commentary`));

  const parts = [text];
  if (verses.length > MAX_VERSES) parts.push(el('p', { class: 'pop-muted' }, `First ${MAX_VERSES} of ${verses.length} verses.`));
  parts.push(actions);

  const xrefs = ref.v1 !== undefined && ref.v1 === ref.v2 && ref.c1 === ref.c2 ? book.x[`${ref.c1}:${ref.v1}`] : null;
  if (xrefs?.length) {
    parts.push(
      el('div', { class: 'pop-section' },
        el('span', { class: 'pop-label' }, 'Often read with'),
        el('span', { class: 'pop-chips' }, xrefs.map(([b, c, v, end]) => {
          const target = { book: b, c1: c, v1: v, c2: c, v2: end ?? v };
          return el('button', { type: 'button', class: 'pop-chip', onclick: () => navigate({ kind: 'ref', value: target }) }, formatRef(target));
        }))
      )
    );
  }

  const studies = await studiesOn(ref);
  if (studies.length) {
    parts.push(
      el('div', { class: 'pop-section' },
        el('span', { class: 'pop-label' }, 'In these studies'),
        el('ul', { class: 'pop-studies' }, studies.map((s) => el('li', {}, el('a', { href: new URL(s.u, SITE).href }, s.t), s.primary ? el('span', { class: 'pop-muted' }, ' · main passage') : null)))
      )
    );
  }

  parts.push(el('p', { class: 'pop-source' }, 'World English Bible (public domain). Cross-references: OpenBible.info (CC BY).'));
  body.replaceChildren(...parts);
}

let studyIndex = null;
async function loadStudies() {
  if (!studyIndex) {
    studyIndex = load('studies.json').then((data) => {
      const byBook = new Map();
      for (const s of data.studies) {
        for (const [list, primary] of [[s.p, true], [s.r, false]]) {
          for (const text of list) {
            const ref = parseRef(text);
            if (!ref) continue;
            if (!byBook.has(ref.book)) byBook.set(ref.book, []);
            byBook.get(ref.book).push({ study: s, primary, range: span(ref) });
          }
        }
      }
      return { byBook, commentary: data.commentary, studies: data.studies, words: data.words ?? {} };
    });
  }
  return studyIndex;
}

async function studiesOn(ref) {
  let index;
  try {
    index = await loadStudies();
  } catch {
    return [];
  }
  const [from, to] = span(ref);
  const here = new URL(window.location.pathname, window.location.origin).pathname;
  const hits = new Map();
  for (const { study, primary, range } of index.byBook.get(ref.book) ?? []) {
    if (range[0] > to || range[1] < from) continue;
    if (new URL(study.u, SITE).pathname === here) continue;
    const seen = hits.get(study.u);
    if (!seen || (primary && !seen.primary)) hits.set(study.u, { ...study, primary });
  }
  return [...hits.values()].sort((a, b) => b.primary - a.primary).slice(0, MAX_STUDIES);
}

async function commentaryUrl(ref) {
  try {
    const { commentary } = await loadStudies();
    const url = commentary[BOOK_ORDER.indexOf(ref.book) + 1]?.[ref.c1];
    return url ? new URL(url, SITE).href : null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------------------------
// Words

async function renderWord(id) {
  const prefix = id[0];
  const number = parseInt(id.slice(1), 10);
  title.textContent = `${prefix === 'H' ? 'Hebrew' : 'Greek'} word · ${id}`;
  card.setAttribute('aria-label', `Word study ${id}`);
  const shard = await load(`words/${prefix}${String(Math.floor(number / 100)).padStart(2, '0')}.json`);
  const word = shard[number];
  if (!word) {
    body.replaceChildren(el('p', { class: 'pop-muted' }, `${id} is not in the lexicon.`));
    return;
  }
  const semitic = word.lang === 'Hebrew' || word.lang === 'Aramaic' || prefix === 'H';
  title.textContent = `${word.lang || (semitic ? 'Hebrew' : 'Greek')} ${word.p} · ${id}`;

  const times = (n) => `${n.toLocaleString()} ${n === 1 ? 'time' : 'times'}`;
  const counts = [];
  if (word.c.ot !== undefined) counts.push(`${times(word.c.ot)} in the Old Testament`);
  if (word.c.nt !== undefined) counts.push(`${times(word.c.nt)} in the New Testament`);
  if (word.c.lxx) counts.push(`${word.c.lxx.toLocaleString()} in the Septuagint`);

  const testament = semitic ? 'Old Testament' : 'New Testament';
  const total = semitic ? word.c.ot : word.c.nt;
  const parts = [
    el('div', { class: 'pop-lemma' },
      el('span', { class: 'pop-script', dir: semitic ? 'rtl' : 'ltr', lang: semitic ? 'he' : 'grc' }, word.l),
      el('span', { class: 'pop-translit' }, word.t.replace(/\./g, '\u00b7'))
    ),
    el('p', { class: 'pop-gloss' }, word.g),
    el('p', { class: 'pop-counts' }, counts.join(' \u00b7 ')),
  ];

  // Where the word is. A rare word lists every verse, and each opens in this card -- which is
  // also how a reader checks a study's "only here" for themselves. A common word shows where it
  // gathers.
  if (word.o?.length) {
    const label = total === 1 ? `The only place in the ${testament}` : `Every place in the ${testament}`;
    parts.push(
      el('div', { class: 'pop-section' },
        el('span', { class: 'pop-label' }, label),
        el('span', { class: 'pop-chips' }, word.o.map(([b, c, v]) => {
          const target = { book: b, c1: c, v1: v, c2: c, v2: v };
          return el('button', { type: 'button', class: 'pop-chip', onclick: () => navigate({ kind: 'ref', value: target }) }, formatRef(target));
        }))
      )
    );
  } else if (word.b?.length) {
    parts.push(
      el('div', { class: 'pop-section' },
        el('span', { class: 'pop-label' }, 'Most often in'),
        el('span', { class: 'pop-chips' }, word.b.map(([b, n]) => el('span', { class: 'pop-chip pop-static' }, `${bookName(b)} `, el('span', { class: 'pop-muted' }, `\u00d7${n}`))))
      )
    );
  }

  const renderings = word.r.filter(([g]) => g && g !== word.g.toLowerCase());
  if (renderings.length) {
    parts.push(
      el('div', { class: 'pop-section' },
        el('span', { class: 'pop-label' }, 'Rendered in context as'),
        el('span', { class: 'pop-chips' }, word.r.map(([g, n]) => el('span', { class: 'pop-chip pop-static' }, `${g} `, el('span', { class: 'pop-muted' }, `\u00d7${n}`))))
      )
    );
  }

  const studies = await studiesUsing(id);
  if (studies.length) {
    parts.push(
      el('div', { class: 'pop-section' },
        el('span', { class: 'pop-label' }, 'Discussed in'),
        el('ul', { class: 'pop-studies' }, studies.map((s) => el('li', {}, el('a', { href: new URL(s.u, SITE).href }, s.t))))
      )
    );
  }

  parts.push(
    el('p', { class: 'pop-source' }, semitic
      ? 'Lexicon: STEPBible.org (CC BY). Counts, places and renderings: MACULA Hebrew (CC BY 4.0).'
      : 'Lexicon: STEPBible.org (CC BY). Counts, places and renderings: MACULA Greek (CC BY 4.0); Septuagint count: Open Scriptures.')
  );
  body.replaceChildren(...parts);
}

async function studiesUsing(id) {
  let index;
  try {
    index = await loadStudies();
  } catch {
    return [];
  }
  const here = new URL(window.location.pathname, window.location.origin).pathname;
  return (index.words[id] ?? [])
    .map((i) => index.studies[i])
    .filter((s) => new URL(s.u, SITE).pathname !== here)
    .slice(0, MAX_STUDIES);
}

// ---------------------------------------------------------------------------------------------
// Wiring

function targetOf(event) {
  const node = event.target instanceof Element ? event.target.closest('.pop-ref, .pop-word') : null;
  return node && refs.has(node) ? node : null;
}

function openFrom(node, pin) {
  clearTimeout(openTimer);
  clearTimeout(closeTimer);
  if (anchor === node && !card.hidden) {
    if (pin && pinned) hide();
    else pinned = pinned || pin;
    return;
  }
  show(refs.get(node), node, pin);
}

function init() {
  const root = document.querySelector('article.md-content__inner');
  if (!root) return;
  scan(root);
  document.body.append(card);
  // The interactive tools render after this scan; they pass their own late-rendered panels here so
  // the references in them pop up like any other.
  window.theWayPopups = { scan: (node) => node && scan(node) };

  document.addEventListener('click', (event) => {
    const node = targetOf(event);
    if (node) {
      event.preventDefault();
      openFrom(node, true);
    } else if (!card.hidden && !event.composedPath().includes(card)) {
      // composedPath, because a click inside the card may re-render it and detach the target.
      hide();
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !card.hidden) {
      pinned = true;
      hide();
      return;
    }
    const node = targetOf(event);
    if (node && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      openFrom(node, true);
      close.focus();
    }
  });

  if (window.matchMedia('(hover: hover)').matches) {
    document.addEventListener('mouseover', (event) => {
      const node = targetOf(event);
      if (node) {
        clearTimeout(closeTimer);
        if (pinned && !card.hidden) return;
        clearTimeout(openTimer);
        openTimer = setTimeout(() => openFrom(node, false), HOVER_OPEN_MS);
      } else if (card.contains(event.target)) {
        clearTimeout(closeTimer);
      }
    });
    document.addEventListener('mouseout', (event) => {
      if (!targetOf(event) && !card.contains(event.target)) return;
      clearTimeout(openTimer);
      if (pinned || card.hidden) return;
      closeTimer = setTimeout(hide, HOVER_CLOSE_MS);
    });
  }

  back.addEventListener('click', () => {
    history.pop();
    render();
  });
  close.addEventListener('click', () => {
    pinned = true;
    hide();
  });
  window.addEventListener('resize', () => place());
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
