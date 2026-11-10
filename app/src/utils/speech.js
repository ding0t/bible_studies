// "Hear it": Hebrew and Greek spoken by the device's own voice (the Web Speech API), for the word
// cards (entries/hebrew-cards.js) and the pop-ups (entries/popups.js). Nothing is recorded or
// downloaded; a device without a Hebrew or Greek voice says so.

const LANG_TAG = { he: 'he-IL', el: 'el-GR' };

// Cantillation, meteg, paseq, sof pasuq and the upper and lower dots guide chanting, not speech.
const HEBREW_MARKS = /[֑-ֽ֯׀׃-ׅ]/g;
const POINTS = '[\\u05B0-\\u05BC\\u05C1\\u05C2\\u05C7]*';
const DIVINE_NAME = new RegExp(`י(${POINTS})ה(${POINTS})ו(${POINTS})ה(${POINTS})`, 'g');
const HIRIQ = 'ִ';

// The divine name is read Adonai and never sounded out, in every pointing the texts use (יְהוָה,
// the lexicon's יְהֹוָה) and after a prefix (לַיהוָה). Pointed with hiriq for Elohim -- after
// Adonai, as in Isaiah 61:1 -- it is read Elohim.
function spokenHebrew(text) {
  return text
    .replace(HEBREW_MARKS, '')
    .replace(/־/g, ' ')
    .replace(DIVINE_NAME, (...m) => (m.slice(1, 5).join('').includes(HIRIQ) ? 'אֱלֹהִים' : 'אֲדֹנָי'));
}

// A modern Greek voice reads monotonic Greek: breathings and the iota subscript go, and the grave
// and circumflex become the one accent it knows.
function spokenGreek(text) {
  return text
    .normalize('NFD')
    .replace(/[̓̔̓ͅ]/g, '')
    .replace(/[̀͂]/g, '́')
    .normalize('NFC');
}

/** lang: 'he' (Hebrew and Aramaic) or 'el' (Greek). */
export function spokenText(text, lang = 'he') {
  return lang === 'he' ? spokenHebrew(text) : spokenGreek(text);
}

export const canSpeak = () => Boolean(globalThis.speechSynthesis && globalThis.SpeechSynthesisUtterance);

/**
 * Speaks one text, or several in turn (a passage, a verse at a time: Chrome stops a single
 * utterance after about fifteen seconds). Calls onUnavailable when the device cannot voice the
 * language. A missing voice in getVoices() is not that: Safari can list none until its voices
 * have loaded and still speak by lang, so the utterance is sent and only an error reports.
 */
export function speak(texts, lang, onUnavailable = () => {}) {
  const { speechSynthesis, SpeechSynthesisUtterance } = globalThis;
  if (!canSpeak()) return onUnavailable();
  const voice = speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith(lang)) ?? null;
  let reported = false;
  speechSynthesis.cancel();
  for (const text of [texts].flat()) {
    const utterance = new SpeechSynthesisUtterance(spokenText(text, lang));
    if (voice) utterance.voice = voice;
    utterance.lang = voice?.lang ?? LANG_TAG[lang];
    utterance.rate = 0.8;
    utterance.onerror = (e) => {
      if (reported || e.error === 'interrupted' || e.error === 'canceled') return;
      reported = true;
      speechSynthesis.cancel();
      onUnavailable();
    };
    speechSynthesis.speak(utterance);
  }
}

// Voices load asynchronously in some browsers; asking once early makes the first "Hear it" find one.
if (canSpeak()) globalThis.speechSynthesis.getVoices();
