/**
 * Bible Reference Parser and Link Generator
 * Converts raw reference text to dynamic links across multiple sources
 */

// Book name mapping
const BOOK_MAP = {
  'genesis': { short: 'gen', num: 1 },
  'exodus': { short: 'exo', num: 2 },
  'leviticus': { short: 'lev', num: 3 },
  'numbers': { short: 'num', num: 4 },
  'deuteronomy': { short: 'deu', num: 5 },
  'joshua': { short: 'jos', num: 6 },
  'judges': { short: 'jdg', num: 7 },
  'ruth': { short: 'rut', num: 8 },
  '1 samuel': { short: '1sa', num: 9 },
  '2 samuel': { short: '2sa', num: 10 },
  '1 kings': { short: '1ki', num: 11 },
  '2 kings': { short: '2ki', num: 12 },
  '1 chronicles': { short: '1ch', num: 13 },
  '2 chronicles': { short: '2ch', num: 14 },
  'ezra': { short: 'ezr', num: 15 },
  'nehemiah': { short: 'neh', num: 16 },
  'esther': { short: 'est', num: 17 },
  'job': { short: 'job', num: 18 },
  'psalm': { short: 'psa', num: 19 },
  'psalms': { short: 'psa', num: 19 },
  'proverbs': { short: 'pro', num: 20 },
  'ecclesiastes': { short: 'ecc', num: 21 },
  'song of solomon': { short: 'sng', num: 22 },
  'song of songs': { short: 'sng', num: 22 },
  'isaiah': { short: 'isa', num: 23 },
  'jeremiah': { short: 'jer', num: 24 },
  'lamentations': { short: 'lam', num: 25 },
  'ezekiel': { short: 'ezk', num: 26 },
  'daniel': { short: 'dan', num: 27 },
  'hosea': { short: 'hos', num: 28 },
  'joel': { short: 'jol', num: 29 },
  'amos': { short: 'amo', num: 30 },
  'obadiah': { short: 'oba', num: 31 },
  'jonah': { short: 'jon', num: 32 },
  'micah': { short: 'mic', num: 33 },
  'nahum': { short: 'nah', num: 34 },
  'habakkuk': { short: 'hab', num: 35 },
  'zephaniah': { short: 'zep', num: 36 },
  'haggai': { short: 'hag', num: 37 },
  'zechariah': { short: 'zec', num: 38 },
  'malachi': { short: 'mal', num: 39 },
  'matthew': { short: 'mat', num: 40 },
  'mark': { short: 'mar', num: 41 },
  'luke': { short: 'luk', num: 42 },
  'john': { short: 'joh', num: 43 },
  'acts': { short: 'act', num: 44 },
  'romans': { short: 'rom', num: 45 },
  '1 corinthians': { short: '1co', num: 46 },
  '2 corinthians': { short: '2co', num: 47 },
  'galatians': { short: 'gal', num: 48 },
  'ephesians': { short: 'eph', num: 49 },
  'philippians': { short: 'php', num: 50 },
  'colossians': { short: 'col', num: 51 },
  '1 thessalonians': { short: '1th', num: 52 },
  '2 thessalonians': { short: '2th', num: 53 },
  '1 timothy': { short: '1ti', num: 54 },
  '2 timothy': { short: '2ti', num: 55 },
  'titus': { short: 'tit', num: 56 },
  'philemon': { short: 'phm', num: 57 },
  'hebrews': { short: 'heb', num: 58 },
  'james': { short: 'jas', num: 59 },
  '1 peter': { short: '1pe', num: 60 },
  '2 peter': { short: '2pe', num: 61 },
  '1 john': { short: '1jo', num: 62 },
  '2 john': { short: '2jo', num: 63 },
  '3 john': { short: '3jo', num: 64 },
  'jude': { short: 'jud', num: 65 },
  'revelation': { short: 'rev', num: 66 },
};

/**
 * Parse Bible reference text into structured data
 * Supports: "Genesis 1:27", "John 3:16-18", "1 Corinthians 13:4-7"
 * @param {string} text - Raw reference text
 * @returns {Object|null} Parsed reference or null if invalid
 */
export const parseReference = (text) => {
  if (!text || typeof text !== 'string') return null;
  
  // Match pattern: [book name] [chapter]:[verse] or [chapter]:[verse]-[verse]
  const regex = /^([\d]?\s*[a-z\s]+)\s+(\d+):(\d+)(?:-(\d+))?$/i;
  const match = text.trim().match(regex);
  
  if (!match) return null;
  
  const bookName = match[1].toLowerCase().trim();
  const chapter = parseInt(match[2]);
  const verseStart = parseInt(match[3]);
  const verseEnd = match[4] ? parseInt(match[4]) : verseStart;
  
  // Find matching book
  const bookInfo = BOOK_MAP[bookName];
  if (!bookInfo) return null;
  
  return {
    book: bookName,
    bookShort: bookInfo.short,
    bookNum: bookInfo.num,
    chapter,
    verses: verseStart === verseEnd ? [verseStart] : Array.from(
      { length: verseEnd - verseStart + 1 },
      (_, i) => verseStart + i
    ),
    display: text,
    firstVerse: verseStart
  };
};

/**
 * Generate Bible link for multiple sources
 * @param {Object} parsedRef - Parsed reference object
 * @param {string} version - Bible version (esv, kjv, etc.)
 * @param {string} site - Target site (blueletterbible, biblegateway, biblehub)
 * @returns {string} Full URL
 */
export const generateBibleLink = (parsedRef, version = 'esv', site = 'blueletterbible') => {
  if (!parsedRef) return null;
  
  const { book, bookShort, chapter, firstVerse, display } = parsedRef;
  
  const urls = {
    blueletterbible: `https://www.blueletterbible.org/${version}/${book}/${chapter}/${firstVerse}/`,
    biblegateway: `https://www.biblegateway.com/passage/?search=${encodeURIComponent(display)}&version=${version.toUpperCase()}`,
    biblehub: `https://biblehub.com/${book}/${chapter}-${firstVerse}.htm`
  };
  
  return urls[site] || urls.blueletterbible;
};

/**
 * Get site display name
 * @param {string} site - Site key
 * @returns {string} Display name
 */
export const getSiteDisplayName = (site) => {
  const names = {
    blueletterbible: 'Blue Letter Bible',
    biblegateway: 'Bible Gateway',
    biblehub: 'BibleHub'
  };
  return names[site] || site;
};
