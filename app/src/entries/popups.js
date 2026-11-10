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
  formKey,
  formShard,
  bareKey,
  lemmaBefore,
  namedWork,
  parseRef,
  parseStrongs,
  resolveRelative,
} from '../utils/scriptureRefs.js';
import { canSpeak, speak } from '../utils/speech.js';

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

// The device's own Hebrew or Greek voice (utils/speech.js). Hidden where the browser has no speech.
function hearButton(texts, lang, label) {
  if (!canSpeak()) return null;
  const button = el('button', {
    type: 'button',
    class: 'pop-link pop-hear',
    title: `Spoken by your device's ${lang === 'he' ? 'Hebrew' : 'Greek'} voice`,
    onclick: () => speak(texts, lang, () => { button.textContent = `No ${lang === 'he' ? 'Hebrew' : 'Greek'} voice on this device`; }),
  }, `\u{1F50A} ${label}`);
  return button;
}

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
  if (kind === 'word') {
    const lang = scriptOf(text);
    if (lang) node.lang = lang;
    else node.classList.add('pop-tag');
  }
  refs.set(node, { kind, value });
  if (kind === 'ref') node.setAttribute('aria-label', `${text.trim()}: show ${formatRef(value)}`);
  else node.setAttribute('aria-label', `${text.trim()}: show word study ${value}`);
  return node;
}

// ---------------------------------------------------------------------------------------------
// Finding references in the page

// A screen reader voices text by its lang, and studies are read aloud: Hebrew left untagged is read
// with an English voice. It also gives hebrew.css the hook for a font that draws vowel points.
const scriptOf = (text) => (/[\u0590-\u05FF\uFB1D-\uFB4F]/.test(text) ? 'he' : /[\u0370-\u03FF\u1F00-\u1FFF]/.test(text) ? 'grc' : null);

function scan(root) {
  for (const span of root.querySelectorAll('[dir="rtl"]:not([lang]):not(.paleo)')) span.lang = 'he';
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
  return linkForms(root);
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

// Every other Greek or Hebrew word on the page -- an inflected form of a tagged word (ὑψωθῆναι beside
// ὑψόω, G5312), a quoted verse, a lemma named with no number -- opens through the form index
// export_popups.py writes from the Hebrew Bible, the Greek NT and the Septuagint. A form that
// belongs to more than one word is linked only when the page has tagged one of them, so the index
// never overrules a study. Single letters (the alphabet tables) are left alone.
const MAQAF = /\u05BE/;
async function linkForms(root) {
  const pending = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        return node.matches(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP;
      }
      return ORIGINAL.test(node.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
    },
  });
  while (walker.nextNode()) {
    const words = [];
    for (const w of findWords(walker.currentNode.data)) {
      let start = w.start;
      for (const part of walker.currentNode.data.slice(w.start, w.end).split(MAQAF)) {
        const key = formKey(part);
        if ([...bareKey(key)].length >= 2) words.push({ start, end: start + part.length, keys: [key, bareKey(key)] });
        start += part.length + 1;
      }
    }
    if (words.length) pending.push({ node: walker.currentNode, words });
  }
  if (!pending.length) return;

  const shards = new Map();
  for (const { words } of pending) for (const w of words) shards.set(formShard(w.keys[0]), null);
  await Promise.all(
    [...shards.keys()].map(async (s) => shards.set(s, await load(`forms/${s}.json`).catch(() => ({}))))
  );
  const onPage = new Set([...root.querySelectorAll('.pop-word')].map((n) => refs.get(n)?.value));
  const resolve = (keys) => {
    for (const key of keys) {
      const found = shards.get(formShard(key))?.[key];
      if (typeof found === 'string') return found;
      if (found) return found.find((id) => onPage.has(id)) ?? null;
    }
    return null;
  };

  for (const { node, words } of pending) {
    if (!node.isConnected) continue;
    const fragment = document.createDocumentFragment();
    let at = 0;
    for (const w of words) {
      const id = resolve(w.keys);
      if (!id) continue;
      fragment.append(node.data.slice(at, w.start), trigger('word', id, node.data.slice(w.start, w.end)));
      at = w.end;
    }
    if (!at) continue;
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
  if (kind === 'word' && !node.hasAttribute('lang')) {
    const lang = scriptOf(node.textContent);
    if (lang) node.lang = lang;
  }
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
    else await renderWord(item.value, item.form, item.morph);
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
    body.replaceChildren(el('p', { class: 'pop-muted' }, `${formatRef(ref)} is not in the ${book.t.name}'s numbering.`));
    return;
  }

  const shown = verses.slice(0, MAX_VERSES);
  const fromFallback = new Set(book.f ?? []);
  const multiChapter = ref.c2 !== ref.c1;
  const testament = BOOK_ORDER.indexOf(ref.book) < BOOK_ORDER.indexOf('Matt') ? 'ot' : 'nt';
  const lens = lensFor(testament);
  const text = el('div', { class: 'pop-text' });
  let chapterShown = null;
  const chapterHeading = (c) => {
    if (multiChapter && c !== chapterShown) {
      text.append(el('span', { class: 'pop-chapter' }, `Chapter ${c}`));
      chapterShown = c;
    }
  };
  let source = `${book.t.name} (${book.t.licence}).`;
  const spoken = [];
  const chapters = new Map();
  await Promise.all(
    [...new Set(shown.map((s) => s.c))].map(async (c) => chapters.set(c, await load(`original/${ref.book}/${c}.json`).catch(() => null)))
  );
  if (lens === 'reading') {
    for (const { c, v, text: words, cited } of shown) {
      chapterHeading(c);
      // A verse the reading text omits is shown from the fallback, and says so.
      const borrowed = fromFallback.has(`${c}:${v}`)
        ? el('span', { class: 'pop-muted', title: book.t.fallback.note }, ` (${book.t.fallback.code}: ${book.t.fallback.note})`)
        : null;
      const linked = borrowed ? words : englishLinked(words, chapters.get(c)?.v[v]);
      text.append(el('span', { class: cited ? 'pop-verse' : 'pop-verse pop-around' }, el('sup', {}, String(v)), ' ', linked, borrowed, ' '));
    }
  } else if (chapters.size && [...chapters.values()].every(Boolean)) {
    source = renderOriginal(text, shown, chapters, lens, testament, chapterHeading, spoken);
  } else {
    text.append(el('p', { class: 'pop-muted' }, 'The original-language text could not be loaded.'));
  }
  const footnotes = shown.filter((s) => s.cited).flatMap(({ c, v }) => (book.n?.[`${c}:${v}`] ?? []).map((n) => (shown.length > 1 ? `${v}: ${n}` : n)));

  const actions = el('div', { class: 'pop-actions' });
  if (spoken.length) {
    const hebrew = (testament === 'ot' && lens !== 'lxx') || lens === 'hebrew-nt';
    actions.append(hearButton(spoken, hebrew ? 'he' : 'el', spoken.length > 1 ? 'Hear the verses' : 'Hear the verse') ?? '');
  }
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
  const linkCounts = ref.v1 !== undefined && ref.v1 === ref.v2 && ref.c1 === ref.c2 ? await scriptureLinksAt(`${ref.book} ${ref.c1}:${ref.v1}`) : null;
  if (linkCounts) {
    const [quotes, quoted] = linkCounts;
    const said = [quotes ? `quotes or echoes ${quotes}` : null, quoted ? `quoted or echoed by ${quoted}` : null].filter(Boolean).join(' · ');
    actions.append(
      el('a', { class: 'pop-link', href: `${new URL('references/', SITE).href}#ref=${encodeURIComponent(`${ref.book} ${ref.c1}:${ref.v1}`)}`, title: said }, `Scripture links (${quotes + quoted})`)
    );
  }
  const chapterUrl = await commentaryUrl(ref);
  if (chapterUrl) actions.append(el('a', { class: 'pop-link', href: chapterUrl }, `${formatRef({ ...ref, v1: undefined, c2: ref.c1 })} commentary`));

  const parts = [lensSwitch(testament, lens, book.t.code), text];
  if (lens !== 'reading') {
    if (text.querySelector('.pop-alt')) parts.push(el('p', { class: 'pop-muted' }, `Numbers in brackets are the ${lens === 'lxx' ? 'Septuagint' : 'Hebrew Bible'}’s own, where it numbers the verse differently.`));
    if (lens === 'lxx' || lens === 'hebrew-nt') linkForms(text);
  }
  if (testament === 'nt' && (lens === 'original' || lens === 'interlinear')) {
    const quoted = septuagintQuoted(shown, chapters);
    if (quoted) parts.push(quoted);
  }
  if (lens === 'reading' && footnotes.length) parts.push(el('ul', { class: 'pop-footnotes' }, footnotes.map((n) => el('li', {}, n))));
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

  parts.push(el('p', { class: 'pop-source' }, `${source} Cross-references: OpenBible.info (CC BY).`));
  body.replaceChildren(...parts);
}

// The verse in the language it was written in. Four lenses on one verse: the reading translation,
// the Hebrew or Greek, the same word by word with the BSB's English under each word, and for the
// Old Testament the Septuagint the apostles quoted. The reader's choice holds for every card after,
// so a reader who wants the Greek gets it without asking again.
const LENS_KEY = 'pop-lens';
function lensFor(testament) {
  let lens = 'reading';
  try {
    lens = window.localStorage.getItem(LENS_KEY) ?? lens;
  } catch {
    // Storage blocked (a private window): every card opens on the reading translation.
  }
  if (lens === 'lxx' && testament === 'nt') return 'original';
  if (lens === 'hebrew-nt' && testament === 'ot') return 'original';
  return lens;
}

function lensSwitch(testament, current, readingCode) {
  const lenses = [
    ['reading', readingCode, `The ${readingCode}, this site's reading translation`],
    ['original', testament === 'ot' ? 'Hebrew' : 'Greek', testament === 'ot' ? 'The Hebrew Bible (WLC)' : 'The Greek New Testament (SBLGNT)'],
    ['interlinear', 'Word by word', `Each ${testament === 'ot' ? 'Hebrew' : 'Greek'} word with the ${readingCode}’s English for it`],
  ];
  if (testament === 'ot') lenses.push(['lxx', 'Septuagint', 'The Greek Old Testament the apostles quoted (Brenton)']);
  else lenses.push(['hebrew-nt', 'Hebrew (1886)', 'Salkinson and Ginsburg’s 1886 translation of the Greek into Hebrew: a translation, not an original']);
  return el('div', { class: 'pop-lenses', role: 'group', 'aria-label': 'Show the verse in' },
    lenses.map(([value, label, hint]) =>
      el('button', {
        type: 'button',
        class: 'pop-lens',
        title: hint,
        'aria-pressed': String(value === current),
        onclick: () => {
          try {
            window.localStorage.setItem(LENS_KEY, value);
          } catch {
            // Not remembered; this card still switches.
          }
          pinned = true;
          render();
        },
      }, label)));
}

// The BSB's own words, each opening the Hebrew or Greek word it renders. The Berean Interlinear
// records where each word's English falls in the verse (export_popups.py english_spans), so the
// reader can point at "one and only" and reach μονογενής.
function englishLinked(verseText, original) {
  const words = Array.isArray(original) ? original : original?.p.flatMap(([, ws]) => ws) ?? [];
  const placed = words.filter((w) => w.length > 6 && w[1]).sort((a, b) => a[5] - b[5]);
  if (!placed.length) return verseText;
  const out = [];
  let at = 0;
  for (const [form, id, morph, english, translit, start, end] of placed) {
    // The spans were measured against the same BSB text; a verse re-exported since is left plain.
    const phrase = english.replace(/[[\]]/g, '').replace(/\s+/g, ' ').trim();
    if (start < at || verseText.slice(start, end).toLowerCase() !== phrase.toLowerCase()) continue;
    out.push(verseText.slice(at, start));
    out.push(el('button', {
      type: 'button',
      class: 'pop-en-w',
      title: `${form} \u00b7 ${translit}`,
      onclick: () => navigate({ kind: 'word', value: id, form: form.replace(/[.,;·:—־׃]+$/, ''), morph: morph || undefined }),
    }, verseText.slice(start, end)));
    at = end;
  }
  out.push(verseText.slice(at));
  return out;
}

// spoken collects the cited verses' text, a verse to an entry, for "Hear the verse".
function renderOriginal(text, shown, chapters, lens, testament, chapterHeading, spoken) {
  const hebrew = (testament === 'ot' && lens !== 'lxx') || lens === 'hebrew-nt';
  const lang = hebrew ? 'he' : 'grc';
  text.classList.add('pop-orig', lens === 'interlinear' ? 'pop-interlinear' : 'pop-running');
  text.lang = lang;
  if (hebrew) text.dir = 'rtl';

  const word = ([form, id, morph, english, translit], shared) => {
    const [, bare, stop] = /^(.*?)([.,;·:—׃]*)$/.exec(form);
    const shownForm = id
      ? el('button', {
          type: 'button',
          class: shared ? 'pop-w pop-shared' : 'pop-w',
          title: [translit, english].filter(Boolean).join(' \u00b7 '),
          onclick: () => navigate({ kind: 'word', value: id, form: bare.replace(/־$/, ''), morph: morph || undefined }),
        }, bare)
      : el('span', {}, bare);
    if (lens !== 'interlinear') return [shownForm, stop, /־$/.test(bare) ? '' : ' '];
    return el('span', { class: 'pop-stack' },
      el('span', {}, shownForm, stop),
      el('span', { class: 'pop-tr', lang: 'en', dir: 'ltr' }, translit || ''),
      el('span', { class: english ? 'pop-en' : 'pop-en pop-none', lang: 'en', dir: 'ltr', title: english ? null : 'Not rendered as a word of its own in the BSB' }, english || '·'));
  };
  const alt = (label) => el('span', { class: 'pop-alt', title: `${lens === 'lxx' ? 'Septuagint' : 'Hebrew Bible'} ${label}` }, `[${label}]`);

  for (const { c, v, cited } of shown) {
    chapterHeading(c);
    const chapter = chapters.get(c);
    const said = [];
    const verse = el('span', { class: cited ? 'pop-verse' : 'pop-verse pop-around' }, el('sup', { dir: 'ltr' }, String(v)), ' ');
    const missing = (note) => verse.append(el('span', { class: 'pop-muted', lang: 'en', dir: 'ltr' }, note));
    if (lens === 'lxx' || lens === 'hebrew-nt') {
      const found = (lens === 'lxx' ? chapter.g : chapter.s)?.[v];
      if (!found) {
        missing(lens === 'lxx'
          ? '(No Septuagint verse is matched to this one: Brenton lacks it, or the Septuagint orders this passage differently.)'
          : '(Not in Salkinson–Ginsburg.)');
      }
      for (const [label, other] of typeof found === 'string' ? [[null, found]] : found?.p ?? []) {
        verse.append(label ? alt(label) : '', label ? ' ' : '', other, ' ');
        said.push(other);
      }
    } else {
      const found = chapter.v[v];
      const shared = new Set(cited ? chapter.q?.[v]?.at(-1)[3] : []);
      if (!found) missing(`(Not in the ${hebrew ? 'Hebrew text' : 'Greek text'}.)`);
      let index = 0;
      for (const [label, words] of Array.isArray(found) ? [[null, found]] : found?.p ?? []) {
        if (label) verse.append(alt(label), ' ');
        verse.append(...words.flatMap((w) => word(w, shared.has(index++))));
        said.push(words.map(([form]) => form).join(' '));
      }
    }
    text.append(verse, ' ');
    if (cited && said.length) spoken.push(said.join(' '));
  }

  if (lens === 'lxx') return 'Septuagint: Brenton’s edition (public domain), at the verse the Hebrew’s number maps to.';
  if (lens === 'hebrew-nt') return 'Hebrew: Salkinson and Ginsburg’s New Testament (1886, public domain), a translation from the Greek. Tap a word for the Old Testament word it uses.';
  const base = hebrew
    ? 'Hebrew: the Westminster Leningrad Codex as the BSB translates it, from the Berean Interlinear (public domain), accents omitted.'
    : 'Greek: the text the BSB translates, from the Berean Interlinear (public domain).';
  return `${base} English for each word: the BSB. Parsing: MACULA (CC BY 4.0). Tap a word for its grammar.`;
}

// A New Testament verse that quotes the Old: the Septuagint verse beside it, with the words the two
// share in order marked on both sides (export_popups.py septuagint_quoted).
function septuagintQuoted(shown, chapters) {
  const entries = shown.filter((s) => s.cited).flatMap(({ c, v }) => (chapters.get(c)?.q?.[v] ?? []).filter(([ref]) => ref));
  if (!entries.length) return null;
  return el('div', { class: 'pop-section' },
    el('span', { class: 'pop-label' }, 'Quotes the Septuagint'),
    entries.map(([english, number, greek, marked]) => {
      const marks = new Set(marked);
      const words = greek.split(' ').flatMap((w, i) => [marks.has(i) ? el('mark', { class: 'pop-shared' }, w) : w, ' ']);
      const target = parseRef(english);
      const passage = el('p', { class: 'pop-orig pop-running', lang: 'grc' }, words);
      linkForms(passage);
      return el('div', { class: 'pop-quote' },
        el('button', { type: 'button', class: 'pop-chip', onclick: () => navigate({ kind: 'ref', value: target }) }, formatRef(target)),
        number !== english.split(' ').at(-1) ? el('span', { class: 'pop-muted' }, ` (Septuagint ${number})`) : '',
        passage);
    }),
    el('p', { class: 'pop-muted' }, 'Highlighted: words the two share in the same order.'));
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

// links.json is written by scripts/build-links-index.js from the Scripture Links data: a verse is
// listed only when that page has something to show for it.
async function scriptureLinksAt(key) {
  try {
    return (await load('links.json'))[key] ?? null;
  } catch {
    return null;
  }
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

async function renderWord(id, form, morph) {
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
  const language = word.lang && word.lang !== 'name' ? word.lang : semitic ? 'Hebrew' : 'Greek';
  title.textContent = `${language} ${word.p} · ${id}`;

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
      el('span', { class: 'pop-translit' }, word.t.replace(/\./g, '\u00b7')),
      hearButton(word.l, semitic ? 'he' : 'el', 'Hear it')
    ),
    el('p', { class: 'pop-gloss' }, word.g),
    el('p', { class: 'pop-counts' }, counts.join(' \u00b7 ')),
  ];

  // A name spelled in both testaments: Jesse is H3448 in the OT and G2421 in the NT.
  for (const other of word.x ?? []) {
    const where = other.ot !== undefined ? `${times(other.ot)} in the Old Testament` : `${times(other.nt)} in the New Testament`;
    parts.push(
      el('p', { class: 'pop-counts' },
        `${other.ot !== undefined ? 'The Hebrew' : 'The Greek'} spelling, `,
        el('button', { type: 'button', class: 'pop-link', onclick: () => navigate({ kind: 'word', value: other.id }) }, other.id),
        `, occurs ${where}.`)
    );
  }

  const parsed = await parseOf(form, prefix, morph);
  if (parsed) parts.push(parsed);
  if (word.w?.length) parts.push(whoItIs(word));

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

  const differs = (await load('renderings.json').catch(() => ({})))[`${prefix}${number}`];
  if (differs) parts.push(translationsDiffer(differs));

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
      ? 'Lexicon, grammar and names: STEPBible.org (CC BY). Counts, places and renderings: MACULA Hebrew (CC BY 4.0); parsing: OSHB.'
      : 'Lexicon, grammar and names: STEPBible.org (CC BY). Counts, places, renderings and parsing: MACULA Greek (CC BY 4.0); Septuagint count: Open Scriptures.')
  );
  body.replaceChildren(...parts);
}

// Where the BSB and the ULT render the word differently, both sides, and the rendering this site
// follows once the author has decided it (alignment_ranking.py writes renderings.json). The ULT's
// renderings are CC BY-SA, so they live in that file alone and carry their own credit line.
function translationsDiffer(d) {
  const side = (name, list) =>
    el('span', { class: 'pop-chips' },
      el('span', { class: 'pop-muted' }, `${name}: `),
      list.map(([g, n]) => el('span', { class: 'pop-chip pop-static' }, `${g} `, el('span', { class: 'pop-muted' }, `\u00d7${n}`))));
  return el('div', { class: 'pop-section' },
    el('span', { class: 'pop-label' }, 'Translations differ here'),
    el('p', { class: 'pop-muted' }, `The BSB and the ULT render it differently ${d.d} of the ${d.n} times both translate it.`),
    side('BSB', d.b),
    side('ULT', d.u),
    d.f ? el('p', {}, `This site follows \u201c${d.f}\u201d (${d.k}). ${d.w}`) : null,
    el('p', { class: 'pop-source' }, 'Renderings: Berean Interlinear (BSB, public domain); unfoldingWord ULT (CC BY-SA 4.0).'));
}

// The grammar of the form on the page, when one parsing covers it: "Noun Accusative Singular
// Masculine Individual -- a male PERSON that is having something done to them". A Hebrew code is
// read a segment at a time, so וַיֹּאמֶר is a conjunction, then the verb. A word opened from a verse
// in the original brings its own code, which is that occurrence's parsing rather than the form's
// commonest one.
async function parseOf(form, prefix, morph) {
  if (!form || !scriptOf(form)) return null;
  const key = formKey(form.trim());
  const code = morph ?? (await load(`parse/${formShard(key)}.json`).catch(() => ({})))[key];
  if (!code) return null;
  const grammar = await load('grammar.json');
  const parts = prefix === 'G' ? [code] : code.slice(1).split('/').map((s) => code[0] + s);
  const readings = parts.map((p) => grammar[p]).filter(Boolean);
  if (readings.length !== parts.length) return null;
  return el('div', { class: 'pop-section' },
    el('span', { class: 'pop-label' }, `This form, ${form.trim()} `, hearButton(form.trim(), prefix === 'H' ? 'he' : 'el', 'Hear it')),
    readings.map(([label, meaning, example]) =>
      el('p', { class: 'pop-grammar' },
        el('strong', {}, label.replace(/\s+:\s+/, ' ')),
        meaning ? ` \u2014 ${meaning.toLowerCase()}` : '',
        example ? el('span', { class: 'pop-muted' }, ` (e.g. \u201c${example}\u201d)`) : ''))
  );
}

// Who a name is. STEP files each individual under the number, so a name shared by several people
// lists them all; the family tree link opens the person on the timeline when this site has them.
function whoItIs(word) {
  // TIPNR's own field names: a "partner" is Sarah and Hagar alike, which "married to" would not say.
  const family = (label, names) => names?.length ? el('span', { class: 'pop-muted' }, ` ${label}: ${names.join(', ')}.`) : '';
  const more = word.wn ? el('p', { class: 'pop-muted' }, `${word.wn - word.w.length} more individuals share this name.`) : '';
  return el('div', { class: 'pop-section' },
    el('span', { class: 'pop-label' }, word.w.length === 1 ? 'Who this is' : 'Who this may be'),
    el('ul', { class: 'pop-studies' }, word.w.map((p) =>
      el('li', {},
        el('strong', {}, p.n), p.d ? ` \u2014 ${p.d.replace(/\.$/, '')}.` : '',
        family('Parents', p.pa), family('Partners', p.sp), family('Children', p.ch),
        p.id ? [' ', el('a', { href: new URL(`timeline/#view=family&person=${p.id}`, SITE).href }, 'Family tree \u2192')] : ''))),
    more
  );
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
  // A word keeps the spelling the reader pointed at, so the card can parse that form.
  const item = refs.get(node);
  if (card.contains(node)) {
    navigate(item.kind === 'word' ? { ...item, form: node.textContent } : item);
    return;
  }
  show(item.kind === 'word' ? { ...item, form: node.textContent } : item, node, pin);
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
      if (node && card.contains(node)) {
        clearTimeout(closeTimer);
      } else if (node) {
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
