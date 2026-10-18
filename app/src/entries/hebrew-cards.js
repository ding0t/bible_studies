// On-screen practice for the Hebrew and Greek word cards. hooks/hebrew_cards.py and
// hooks/greek_cards.py render each deck with its cards as JSON in
// <script type="application/json" class="hc-data"> and an empty .hc-screen; this fills the
// .hc-screen with one card at a time and a spaced-review session (utils/cardReview.js). A Greek
// deck says so in its JSON (lang, dir, voice, store); a Hebrew deck predates those keys, so each
// falls back to Hebrew.
//
// Progress is a per-browser convenience, kept in localStorage: it can be missing or blocked, so
// every read and write is guarded and the page works without it.
import { review, sessionQueue, spokenText } from '../utils/cardReview.js';

const DAY_KEY = () => new Date().toISOString().slice(0, 10);

function load(key) {
  try {
    return JSON.parse(globalThis.localStorage.getItem(key)) ?? {};
  } catch {
    return {};
  }
}

function save(key, value) {
  try {
    globalThis.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Private window or blocked storage: the session still runs, it just is not remembered.
  }
}

const { speechSynthesis, SpeechSynthesisUtterance } = globalThis;

function findVoice(prefix) {
  return speechSynthesis?.getVoices().find((v) => v.lang.toLowerCase().startsWith(prefix)) ?? null;
}

function speak(text, prefix) {
  const voice = findVoice(prefix);
  if (!voice) return false;
  const utterance = new SpeechSynthesisUtterance(prefix === 'he' ? spokenText(text) : text);
  utterance.voice = voice;
  utterance.lang = voice.lang;
  utterance.rate = 0.8;
  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
  return true;
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  node.append(...children.filter((c) => c != null));
  return node;
}

// Syllables with the stressed one underlined, as on the printed card; a one-syllable word has
// nowhere else for the stress to fall, so it is not marked.
function reading(card) {
  const out = el('p', { class: 'hc-screen-reading' });
  card.words.forEach((w, i) => {
    if (i) out.append('   ');
    if (card.divine && !w.t.length) return out.append(w.strongs === 'H3069' ? 'read Elohim' : 'read Adonai');
    w.t.forEach((syl, j) => {
      if (j) out.append('·');
      out.append(j === w.s && w.t.length > 1 ? el('u', {}, syl) : syl);
    });
  });
  return out;
}

function mount(deck) {
  const data = JSON.parse(deck.querySelector('.hc-data').textContent);
  const screen = deck.querySelector('.hc-screen');
  const lang = data.lang ?? 'he';
  const dir = data.dir ?? 'rtl';
  const voice = data.voice ?? 'he';
  const key = `${data.store ?? 'hebrew-cards'}:${data.slug}`;
  const wordOf = (card) => card.word ?? card.hebrew;
  const secondOf = (card) => card.second ?? card.words.map((w) => w.paleo).join(' ');
  const cards = Object.fromEntries(data.cards.map((c) => [c.id, c]));
  const ids = data.cards.map((c) => c.id);

  let state = load(key);
  state.progress ??= {};
  if (state.day !== DAY_KEY()) Object.assign(state, { day: DAY_KEY(), newToday: 0 });
  let queue = sessionQueue(ids, state.progress, Date.now(), state.newToday);
  let flipped = false;

  function answer(correct) {
    const id = queue.shift();
    if (!state.progress[id]) state.newToday += 1;
    state.progress[id] = review(state.progress[id], correct, Date.now());
    if (!correct) queue.push(id);
    save(key, state);
    flipped = false;
    render();
  }

  function render() {
    const learned = ids.filter((id) => state.progress[id]).length;
    const status = el('p', { class: 'hc-screen-status' },
      `${queue.length} to review now · ${learned} of ${ids.length} cards started`);
    if (!queue.length) {
      screen.replaceChildren(status, el('p', { class: 'hc-screen-done' },
        'Nothing more is due today. Come back tomorrow: the cards you have learned will return when they are due.'));
      return;
    }
    const card = cards[queue[0]];
    const hear = el('button', { type: 'button', class: 'md-button', onclick: () => {
      if (!speak(wordOf(card), voice)) hear.textContent = `No ${lang === 'he' ? 'Hebrew' : 'Greek'} voice on this device`;
    } }, 'Hear it');
    const face = el('div', { class: 'hc-screen-card', lang },
      el('p', { class: 'hc-word', dir }, wordOf(card)),
      el('p', { class: 'hc-paleo', dir }, secondOf(card)),
      flipped ? el('div', { class: 'hc-screen-back', lang: 'en' },
        reading(card),
        el('p', { class: 'hc-meaning' }, card.meaning),
        el('p', { class: 'hc-screen-name' }, card.name + (card.popular ? ` · also “${card.popular}”` : '')),
        el('p', { class: 'hc-screen-quote' }, `${card.quote} (${card.quote_ref}, ESV)`)) : null);
    const actions = flipped
      ? el('div', { class: 'hc-screen-actions' },
        el('button', { type: 'button', class: 'md-button', onclick: () => answer(false) }, 'Again'),
        el('button', { type: 'button', class: 'md-button md-button--primary', onclick: () => answer(true) }, 'I read it'),
        hear)
      : el('div', { class: 'hc-screen-actions' },
        el('button', { type: 'button', class: 'md-button md-button--primary', onclick: () => { flipped = true; render(); } }, 'Show the reading'),
        hear);
    screen.replaceChildren(status, face, actions);
  }

  render();
}

// Voices load asynchronously in some browsers; asking once early makes the first "Hear it" work.
speechSynthesis?.getVoices();
document.querySelectorAll('.hc-deck').forEach(mount);
