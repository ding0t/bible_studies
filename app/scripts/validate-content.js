#!/usr/bin/env node

/**
 * Validates markdown content files for common issues
 * Run with: node scripts/validate-content.js
 */

import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const REPO_ROOT = path.join(__dirname, '../..');
const CONTENT_DIR = path.join(REPO_ROOT, 'docs/content');

let hasErrors = false;
let warningCount = 0;

// Last commit date per content path, for check 17. One `git log` pass over the whole tree rather
// than one per file -- 500-odd git spawns would dominate the runtime of an otherwise instant
// linter. Paths are as-committed, so a file renamed and not yet re-committed simply won't appear
// here and the check skips it, which is the right call: there is nothing to be out of date with.
// Returns an empty map outside a git checkout (a tarball download, say) so the linter still runs.
function lastCommitDates() {
  const dates = new Map();
  let out;
  try {
    out = execFileSync('git', ['log', '--date=short', '--format=%ad', '--name-only', '--', 'docs/content'], {
      cwd: REPO_ROOT,
      encoding: 'utf-8',
      maxBuffer: 64 * 1024 * 1024,
    });
  } catch {
    return dates;
  }
  let currentDate = null;
  for (const line of out.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
      currentDate = trimmed;
    } else if (currentDate && !dates.has(trimmed)) {
      // git log is newest-first, so the first sighting of a path is its latest commit.
      dates.set(trimmed, currentDate);
    }
  }
  return dates;
}

const LAST_COMMIT_DATES = lastCommitDates();

function log(type, file, message) {
  const relativePath = path.relative(process.cwd(), file);
  if (type === 'error') {
    console.error(`❌ ERROR: ${relativePath}`);
    console.error(`   ${message}\n`);
    hasErrors = true;
  } else if (type === 'warning') {
    console.warn(`⚠️  WARNING: ${relativePath}`);
    console.warn(`   ${message}\n`);
    warningCount++;
  }
}

function validateFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  // Handle both Unix (LF) and Windows (CRLF) line endings
  const lines = content.split(/\r?\n/);

  // Check 1: Frontmatter must start on line 1
  if (lines[0].trim() !== '---') {
    if (lines[0].trim() === '' && lines[1]?.trim() === '---') {
      log('error', filePath, 'Frontmatter must start on line 1 (no blank lines before ---)');
    } else {
      log('error', filePath, 'File must start with frontmatter (---) on line 1');
    }
    return;
  }

  // Find the end of frontmatter
  let frontmatterEnd = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      frontmatterEnd = i;
      break;
    }
  }

  if (frontmatterEnd === -1) {
    log('error', filePath, 'Frontmatter closing --- not found');
    return;
  }

  const frontmatter = lines.slice(1, frontmatterEnd).join('\n');

  // Check 2: Must have title
  if (!frontmatter.match(/^title:\s*["']?.+["']?\s*$/m)) {
    log('error', filePath, 'Missing required "title" field in frontmatter');
  }

  // Check 3: Warn if no category
  if (!frontmatter.match(/^category:/m)) {
    log('warning', filePath, 'No "category" field - will default to "other"');
  }

  // Check 4: Warn if no description
  if (!frontmatter.match(/^description:/m)) {
    log('warning', filePath, 'No "description" field - consider adding one for better SEO');
  }

  // Check 5: Check draft status
  const draftMatch = frontmatter.match(/^draft:\s*(true|false)\s*$/m);
  if (!draftMatch) {
    log('warning', filePath, 'No "draft" field - will default to false (published)');
  }

  // Check 6: Validate tags format
  const tagsMatch = frontmatter.match(/^tags:\s*\[.*\]\s*$/m);
  if (tagsMatch) {
    const tagsLine = tagsMatch[0];
    // Check for proper string quoting
    if (tagsLine.includes('[') && !tagsLine.includes('"') && !tagsLine.includes("'")) {
      log('warning', filePath, 'Tags should be quoted strings in the array');
    }
  }

  // Check 7: Validate image paths
  const bodyContent = lines.slice(frontmatterEnd + 1).join('\n');
  const imageMatches = bodyContent.matchAll(/!\[.*?\]\(([^)]+)\)/g);
  for (const match of imageMatches) {
    const imagePath = match[1];
    // Skip external URLs
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      continue;
    }
    // Check for incorrect relative paths (should use assets/img not just img)
    if (imagePath.includes('../img/') && !imagePath.includes('assets/img')) {
      log('error', filePath, `Image path "${imagePath}" appears incorrect - should use "../../assets/img/" from content subdirectories`);
    }
    // Resolve and check if file exists
    if (!imagePath.startsWith('http')) {
      const imageFullPath = path.resolve(path.dirname(filePath), imagePath);
      if (!fs.existsSync(imageFullPath)) {
        log('error', filePath, `Referenced image does not exist: ${imagePath}`);
      }
    }
  }

  // Check 8: Scripture quote block format. A blockquote that quotes Bible text should
  // open with "> ✝️ Reference (TRANSLATION)" as its first line -- see the develop-bible-study
  // skill's Phase 7 quote-block format (e.g. docs/content/studies/prophecy-fulfilled-in-jesus/
  // as-the-snake-was-lifted.md). Detected heuristically: any contiguous run of "> " lines whose
  // combined text names a known translation in parens is treated as a scripture quote block.
  const bodyLines = lines.slice(frontmatterEnd + 1);
  const translationTag = /\((ESV|WEB|NASB|NIV|ASV|YLT|NKJV|KJV|CSB|BSB)\)/;
  let quoteBlock = [];
  let quoteBlockStartLine = 0;

  const checkQuoteBlock = (block, startLine) => {
    if (block.length === 0) return;
    const fullText = block.join(' ');
    if (!translationTag.test(fullText)) return; // not a scripture citation block
    const firstLine = block[0].trim();
    if (!firstLine.startsWith('> ✝️')) {
      log(
        'warning',
        filePath,
        `Line ${startLine + 1}: scripture quote block doesn't open with "> ✝️ Reference (TRANSLATION)" as its first line -- see the develop-bible-study skill's quote-block format`
      );
    }
  };

  bodyLines.forEach((line, i) => {
    if (line.trim().startsWith('>')) {
      if (quoteBlock.length === 0) quoteBlockStartLine = i;
      quoteBlock.push(line);
    } else {
      checkQuoteBlock(quoteBlock, quoteBlockStartLine);
      quoteBlock = [];
    }
  });
  checkQuoteBlock(quoteBlock, quoteBlockStartLine); // trailing block at end of file

  // Check 9: Hebrew/Aramaic text must never be wrapped in markdown bold ("**...**").
  // Synthetic/faux bold (applied when a font has no real bold weight for a script --
  // true of Hebrew niqqud/vowel points in most web font stacks) breaks combining-mark
  // positioning, and the site's one known-good example of inline Hebrew
  // (docs/content/about/why-ai-assisted-study.md) instead wraps the Hebrew itself in
  // <span dir="rtl">...</span>, left unbolded -- see the develop-bible-study skill's
  // style-guide.md for the fuller writeup and worked example. This regex tolerates one
  // level of nested *italic* (e.g. a transliteration) inside the bold span.
  const hebrewCharClass = '\\u0590-\\u05FF';
  const boldSpanPattern = new RegExp(`\\*\\*((?:[^*\\n]|\\*[^*\\n]*\\*)*)\\*\\*`, 'g');
  const hebrewTest = new RegExp(`[${hebrewCharClass}]`);
  let boldMatch;
  while ((boldMatch = boldSpanPattern.exec(bodyContent)) !== null) {
    if (hebrewTest.test(boldMatch[1])) {
      const lineNum = bodyContent.slice(0, boldMatch.index).split(/\r?\n/).length + frontmatterEnd + 1;
      log(
        'error',
        filePath,
        `Line ${lineNum}: Hebrew/Aramaic text is wrapped in markdown bold ("**...**") -- this breaks rendering (see style-guide.md's "Hebrew/RTL text and markdown bold" section). Wrap the Hebrew itself in <span dir="rtl">...</span> instead, and put any bold on the English lead-in text, not the Hebrew glyphs.`
      );
    }
  }

  // Check 10: the "worth ___" narrating-the-argument template. WARNING, not error, and
  // deliberately so -- see style-guide.md's "`worth ___` is a template, not a phrase".
  // Unlike every other tell on that page this one is a template with an open slot
  // ("worth noting/stating/being clear/flagging/..."), so a fixed word list can't catch
  // it; an audit found the other eight phrase families at 0-3 instances each and this one
  // at 47. About a third of those are load-bearing (e.g. "Each proposal is worth stating
  // and declining" signals the structure of what follows), which is exactly why this must
  // stay a warning: a check that fires on legitimate prose trains people to ignore it, and
  // then to ignore the errors next to it. The author decides per hit; the check only
  // guarantees the decision gets made.
  // Two arms, because the slot is open: an explicit list of the commonest fillers, plus a
  // generic "<subject> is worth <anything>ing" that catches fillers nobody has thought of yet.
  // Listing only the known fillers would repeat the exact mistake this check exists to fix.
  // The generic arm was originally anchored to "it is/it's" and missed every other subject --
  // a review of prayer-as-communion.md found "which is worth knowing before building a practice
  // on it", which matched neither arm ("knowing" is not in the list, and the subject is not "it").
  // So the subject slot now accepts it/this/that/which/there, and a bare "is worth ...ing" too.
  // KNOWN AND ACCEPTED TRADE-OFF: leaving the verb slot open also catches the ordinary sense of
  // "worth" -- deserving of -- as in sorcery.md's "nor that their power is worth fearing" or
  // "both are worth following". Those are not the announcing template and should be kept. That is
  // fine: this is a WARNING, and the check's job is to make the author decide, not to decide for
  // them. Do not narrow the verb slot to a fixed list to remove them -- that reintroduces exactly
  // the blind spot documented above, where "knowing" was missing and a filler shipped unflagged.
  const worthPattern = new RegExp(
    [
      String.raw`\bworth\s+(?:being\s+clear|noting|stating|saying|asking|making|pointing\s+out|flagging|remembering|mentioning|bearing\s+in\s+mind|a\s+mention|repeating|emphasi[sz]ing)\b`,
      String.raw`\b(?:it|this|that|which|there)?\s*(?:'s|’s|\bis|\bare|\bwas|\bwere)\s+worth\s+\w+ing\b`,
    ].join('|'),
    'gi'
  );
  let worthMatch;
  while ((worthMatch = worthPattern.exec(bodyContent)) !== null) {
    const lineNum = bodyContent.slice(0, worthMatch.index).split(/\r?\n/).length + frontmatterEnd + 1;
    log(
      'warning',
      filePath,
      `Line ${lineNum}: "${worthMatch[0]}" announces a point instead of making it (style-guide.md, "\`worth ___\` is a template, not a phrase"). Delete it and re-read the sentence -- if nothing is lost it was filler, and check for a doubled claim underneath. Keep it only where it signals the structure of what follows.`
    );
  }

  // Check 11: the "virtue contrast" -- doing the honest thing "rather than" a straw
  // alternative nobody proposed ("stated plainly rather than smoothing it over", "a
  // textual difficulty rather than hiding one", "a reader should know that rather than
  // discover it"). See style-guide.md's "narrating your own editorial virtue". WARNING,
  // for the same reason as Check 10: the identical wording is legitimate when it is an
  // instruction to the READER ("Note anything that doesn't fit cleanly, rather than
  // smoothing it over") rather than the writer describing his own conduct. No regex can
  // tell those apart -- roughly half the corpus hits are the legitimate kind -- so the
  // check surfaces the decision and the author makes it.
  // Two arms. The first is the plain "X rather than Y" form. The second catches the split
  // construction "I'd rather name these plainly than pretend they aren't there", where the
  // verb phrase sits between "rather" and "than" -- the exact shape that let
  // about/why-ai-assisted-study.md pass Check 11 clean. The second arm's "than" verb list
  // is deliberately narrow (no "flatten"/"discover") because a wide list would fire on
  // ordinary preference statements like "I'd rather walk than drive"; as written it has
  // zero false positives across the corpus.
  const virtuePattern = /\brather\s+than\s+(?:smooth(?:ing|ed)?|bury(?:ing)?|hid(?:ing|e)|conceal(?:ing)?|gloss(?:ing)?(?:\s+over)?|flatten(?:ing)?|discover(?:ing)?|pretend(?:ing)?|overclaim(?:ing)?|letting\s+it\s+stand|leaving\s+it\s+(?:there|unsaid))\b|\brather\b(?:\s+\w+){1,6}\s+than\s+(?:pretend|hid|conceal|smooth|bury|gloss|overclaim)\w*/gi;
  let virtueMatch;
  while ((virtueMatch = virtuePattern.exec(bodyContent)) !== null) {
    const lineNum = bodyContent.slice(0, virtueMatch.index).split(/\r?\n/).length + frontmatterEnd + 1;
    log(
      'warning',
      filePath,
      `Line ${lineNum}: "${virtueMatch[0]}" reads as a virtue contrast -- naming a dishonest alternative nobody proposed, so an ordinary statement looks principled (style-guide.md, "narrating your own editorial virtue"). Cut the contrast and keep the fact. Legitimate only when instructing the READER what to do, not describing your own conduct.`
    );
  }

  // Check 12: bullets that are secretly essays. A bullet is a promise of brevity, and
  // breaking it is worse than not having used one -- see style-guide.md's "Structural
  // readability". Threshold is deliberately high (100 words, vs the ~60 the prose guidance
  // suggests): 60 would fire on 28 bullets corpus-wide, many of them judgment calls, while
  // 100 fires on 10 that are indefensible by inspection (the worst is a single 344-word
  // bullet in last-things/rapture.md). A near-zero-false-positive warning gets acted on; a
  // chatty one gets filtered out along with the checks either side of it. Blockquote lines
  // are skipped -- a long quoted verse inside a list is the source's length, not the
  // author's.
  // Check 13: reader-reassurance address -- telling the reader how to feel about a
  // disclosure instead of just making it ("You deserve to know that", "rest assured").
  // See style-guide.md's "The apologia posture". This is the only mechanically detectable
  // part of a defect that is otherwise document-level: about/why-ai-assisted-study.md was
  // an apologia from top to bottom and tripped none of Checks 10-12. WARNING, because
  // "let me be clear" occasionally introduces a genuine clarification.
  const reassurePattern = /\byou\s+(?:deserve|have\s+a\s+right)\s+to\s+know\b|\brest\s+assured\b|\byou\s+can\s+(?:trust|be\s+confident)\s+that\b|\b(?:let\s+me|I\s+want\s+to)\s+be\s+clear\b|\bto\s+be\s+clear\s+with\s+you\b/gi;
  let reassureMatch;
  while ((reassureMatch = reassurePattern.exec(bodyContent)) !== null) {
    const lineNum = bodyContent.slice(0, reassureMatch.index).split(/\r?\n/).length + frontmatterEnd + 1;
    log(
      'warning',
      filePath,
      `Line ${lineNum}: "${reassureMatch[0]}" tells the reader how to feel about a disclosure instead of making it (style-guide.md, "The apologia posture"). Defending against an implied deception implies there is one. State the fact and stop.`
    );
  }

  const BULLET_WORD_LIMIT = 100;
  bodyLines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!/^([-*+]|\d+\.)\s+/.test(trimmed) || trimmed.startsWith('>')) return;
    const words = trimmed.split(/\s+/).length;
    if (words > BULLET_WORD_LIMIT) {
      log(
        'warning',
        filePath,
        `Line ${i + frontmatterEnd + 2}: bullet is ${words} words -- that is a paragraph wearing a bullet's clothes (style-guide.md, "Structural readability"). Promote it to prose under a sub-heading, or split it into several real bullets.`
      );
    }
  });

  // Checks 14-16: how long the opening makes a reader wait for the point, and what it
  // makes them wade through on the way. These exist because reader feedback on
  // feasts/last-supper-four-cups.md was "too much reading to get to the main point" while
  // every standard readability formula rated that study fine -- Flesch 60.0, grade 10.5,
  // mid-pack against its peers. Flesch counts syllables per word and words per sentence;
  // it cannot see time-to-payoff, and it actively rewards a short unfamiliar word ("Seder",
  // two syllables) over the plain phrase that explains it. Rewriting that intro moved its
  // Flesch score DOWN (70.5 -> 66.2) while making it materially easier to read, so a
  // readability gate would have passed the version readers complained about and flagged the
  // fix as a regression. Hence: measure the structural facts, never score the prose.
  //
  // All three are scoped to studies -- frontmatter carries primary_passage, body over 400
  // words -- which excludes the ~390 generated commentary pages, index/tag pages, and the
  // short narrative pieces under god/dreams-and-visions/. All three are WARNINGS, in the
  // spirit of Checks 10-13: each has a legitimate exception the regex cannot see.
  const isStudy =
    /^primary_passage:/m.test(frontmatter) &&
    bodyContent.split(/\s+/).filter((w) => /[A-Za-z]/.test(w)).length >= 400;

  if (isStudy) {
    // A bold run is how this site states an opening thesis, so it doubles as a machine-
    // readable marker for "the point starts here". Bold spans hard-wrapped lines constantly
    // in this corpus, so the pattern must cross a single newline but stop at a blank line --
    // a naive [^*\n]+ under-reports badly (it read last-supper's thesis as 416 words in
    // rather than 180). Prose before the first bold run is the reader's toll.
    //
    // Tuning: all 34 studies have a bold lead; median 206 words, p75 250. A 250 threshold
    // fires on 8, several of which are fine (a study earning its thesis with a scene first
    // is a legitimate shape). 300 fires on 4, each indefensible by inspection -- the worst
    // is jesus/woman-suffering-bleeding.md at 429. Raise this only with a fresh audit.
    const THESIS_WORD_LIMIT = 300;
    const boldLead = /\*\*(?:[^*\n]|\n(?!\s*\n))+?\*\*/.exec(bodyContent.replace(/^#.*$/gm, ''));
    const wordsToThesis = boldLead
      ? bodyContent
          .replace(/^#.*$/gm, '')
          .slice(0, boldLead.index)
          .split(/\s+/)
          .filter((w) => /[A-Za-z]/.test(w)).length
      : Infinity;
    if (wordsToThesis > THESIS_WORD_LIMIT) {
      log(
        'warning',
        filePath,
        `Opening runs ${wordsToThesis === Infinity ? 'the whole study' : wordsToThesis + ' words'} before it states a point in bold. A reader should not have to take the argument on faith that long -- say what the study concludes, then spend the rest earning it.`
      );
    }

    // Check 15: an opening that is mostly other people's words. Scripture up front is fine;
    // 250 words of it before the study says anything is the reader reading the Bible, not
    // the study. Threshold 40% of the first 250 words fires on 2 of 34.
    let openingWords = 0;
    let quotedWords = 0;
    for (const line of bodyLines) {
      if (openingWords >= 250) break;
      const lw = line.split(/\s+/).filter((w) => /[A-Za-z]/.test(w)).length;
      if (line.trim().startsWith('>')) quotedWords += Math.min(lw, 250 - openingWords);
      openingWords += lw;
    }
    const quotedShare = Math.round((quotedWords / Math.min(openingWords, 250)) * 100);
    if (quotedShare > 40) {
      log(
        'warning',
        filePath,
        `${quotedShare}% of the opening 250 words are block quote. Give the reader your reason for quoting before the quote, or the passage is just text they have to hold until you tell them why.`
      );
    }

    // Check 16: a term the reader may not own, in the first 150 words, unglossed. This is
    // the defect Flesch is blindest to -- "Seder" scores BETTER than "the Passover meal's
    // order of service". The list is deliberately short and specific to this site's habits;
    // add to it when a study introduces a new term of art. A gloss counts if it follows
    // within 120 characters, in any of the shapes this corpus already uses: a parenthetical,
    // an em-dash or comma appositive, or an explicit "Hebrew/Greek for". Fires on 2 of 34.
    const JARGON = [
      'seder', 'liturgy', 'exegesis', 'exegetical', 'hermeneutic', 'hermeneutics',
      'eschatology', 'eschatological', 'pericope', 'masoretic', 'septuagint', 'typology',
      'antitype', 'soteriology', 'dispensational', 'dispensationalism', 'apocalyptic',
      'midrash', 'halakha', 'koinonia', 'propitiation', 'eisegesis', 'chiasm', 'chiastic',
      'inclusio', 'protoevangelium'
    ];
    const openingProse = bodyContent
      .replace(/^#.*$/gm, '')
      .split(/\s+/)
      .filter((w) => /[A-Za-z]/.test(w))
      .slice(0, 150)
      .join(' ');
    for (const term of JARGON) {
      const hit = new RegExp(`\\b${term}\\b`, 'i').exec(openingProse);
      if (!hit) continue;
      const after = openingProse.slice(hit.index, hit.index + 120);
      const glossed = /\(|\s--\s|\s—\s|,\s(?:the|a|an)\s|\b(?:Hebrew|Greek|Aramaic|Latin)\s+for\b|\bmeans\b/i.test(after);
      if (!glossed) {
        log(
          'warning',
          filePath,
          `"${hit[0]}" appears in the first 150 words with no gloss. A reader who does not own the word stops reading there. Explain it in the sentence that uses it, or move it past the opening.`
        );
      }
    }
  }

  // Check 20: prose that cannot be read aloud. These studies get read to families and taught
  // from; the New Testament letters were written to be read to a gathered church, which is why
  // they are easy to say and this corpus was not. A reader tried reading bride-of-christ.md to
  // his wife and stopped -- "it sounds too vague and sparse... a sentence that has a lot of words
  // but didn't have much substance".
  //
  // AVERAGE LENGTH IS NOT THE SIGNAL and checking it would find nothing: bride-of-christ averaged
  // 25.0 words against Ephesians 5's 23.4. What separates them is the MEDIAN and the long tail.
  // Romans 12 averages 20.2 with a median of 10 -- half its sentences are ten words or shorter, so
  // a point lands and is then developed. Uniform mid-length prose has no rhythm and nothing lands.
  // Measured on the WEB text: Eph 5 median 20 / 16.7% at >=35w; Rom 12 median 10 / 15.0%;
  // Phil 4 median 15 / 7.4%; 1 Cor 13 median 13 / 6.7%.
  //
  // Thresholds sit just outside the worst Pauline chapter measured, so Paul himself would pass:
  // median >= 22, or >= 25% of sentences at 35+ words. Both are WARNINGS -- a dense evidence
  // section legitimately runs long, and the author decides per file.
  //
  // Only prose paragraphs are counted. Block quotes are the source's sentence length and not the
  // author's; tables, code fences, headings and list items have their own conventions and Check 12
  // already covers bullet length.
  const proseLines = [];
  let inFence = false;
  for (const rawLine of bodyContent.split(/\r?\n/)) {
    if (/^\s*```/.test(rawLine)) { inFence = !inFence; continue; }
    if (inFence) continue;
    if (/^\s*[>|#]/.test(rawLine)) continue;
    if (/^\s*(?:[-*+]|\d+\.)\s/.test(rawLine)) continue;
    if (/^\s*$/.test(rawLine)) { proseLines.push(''); continue; }
    proseLines.push(rawLine.trim());
  }
  // Paragraph-bounded: a paragraph ending in a colon (introducing a block quote) would otherwise
  // be joined to the next one, inventing sentences that nobody wrote and inflating both numbers.
  const proseText = proseLines
    .join('\n')
    .split(/\n\s*\n/)
    .map((para) => (/[.!?]["')\]]*\s*$/.test(para.trim()) ? para : `${para.trim()}.`))
    .join('\n\n')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')   // links -> their text
    .replace(/[*_`]/g, '')
    .replace(/<[^>]+>/g, '')
    // protect the abbreviations and references that would otherwise split a sentence
    .replace(/\b(vv?|cf|e\.g|i\.e|Gk|Heb|Lit|St|Mt|Mk|Lk|Jn|ch|chs|p|pp|ed|trans|c)\.\s/gi, '$1<DOT> ')
    .replace(/(\d)\.\s(?=\d)/g, '$1<DOT> ');
  const sentences = proseText
    .split(/(?<=[.!?])["')\]]*\s+(?=[A-Z"'\u201c(])/)
    .map((x) => x.replace(/<DOT>/g, '.').trim())
    .filter((x) => x.split(/\s+/).filter(Boolean).length > 3);
  if (sentences.length >= 25) {
    const lengths = sentences.map((x) => x.split(/\s+/).filter(Boolean).length).sort((a, b) => a - b);
    const mid = Math.floor(lengths.length / 2);
    const median = lengths.length % 2 ? lengths[mid] : Math.round((lengths[mid - 1] + lengths[mid]) / 2);
    const longOnes = lengths.filter((n) => n >= 35).length;
    const longPct = (100 * longOnes) / lengths.length;
    if (median >= 22 || longPct >= 25) {
      log(
        'warning',
        filePath,
        `Reads as written-to-be-scanned, not read aloud: median sentence ${median} words, ${longPct.toFixed(0)}% at 35+ words (${longOnes} of ${lengths.length}). Paul's own range is median 10-20 and 7-17% -- Romans 12 averages 20 words with a median of 10, because half its sentences are short enough to land. Break the longest sentences at their "and", semicolon or dash, put the point in a short sentence of its own, and read the result out loud. See style-guide.md rule 7.`
      );
    }
  }

  // Check 18: exhaustiveness claims about an original-language word. "The only occurrence",
  // "nowhere else", "appears once" -- the cheapest sentences in a study to write and the most
  // expensive to verify, so they are routinely written unverified. This one shipped: a study said
  // byssinos "clothes nobody else in the book" when Babylon wears it six verses earlier.
  //
  // The check cannot verify the claim; nothing in Node can reach the Greek database. It asks. It
  // fires only when the exhaustiveness language shares a line with Greek or Hebrew characters,
  // which keeps it off ordinary prose, and it is a warning because the claim is often true.
  {
    const EXHAUSTIVE = /\b(only occurrence|only place|only time|nowhere else|appears once|occurs once|the sole|never elsewhere|no other (?:verse|passage|book)|clothes nobody|used nowhere)\b/i;
    const ORIGINAL_SCRIPT = /[\u0370-\u03FF\u1F00-\u1FFF\u0590-\u05FF]/;
    bodyLines.forEach((line, i) => {
      if (EXHAUSTIVE.test(line) && ORIGINAL_SCRIPT.test(line)) {
        log(
          'warning',
          filePath,
          `Line ${i + frontmatterEnd + 2}: an exhaustiveness claim about an original-language word ("${(line.match(EXHAUSTIVE) || [''])[0]}"). Re-run the count before publishing -- these are written unverified more often than any other kind, and one shipped saying a word "clothes nobody else in the book" when it clothes Babylon.`
        );
      }
    });
  }

  // Check 19: a directional reference next to an internal link that points the wrong way.
  // "See [X](#x) above" when #x is below is invisible to every other check here -- mkdocs resolves
  // the anchor, so --strict passes, and the reader is simply sent the wrong way. Reordering a study
  // breaks these silently and in bulk: a section move broke five in one file, and three more had
  // been wrong beforehand.
  {
    const headingLine = new Map();
    bodyLines.forEach((line, i) => {
      const h = line.match(/^#{2,4}\s+(.*)$/);
      if (h) {
        const slug = h[1]
          .toLowerCase()
          .replace(/[`*_]/g, '')
          .replace(/[^\w\s-]/g, '')
          .trim()
          .replace(/\s+/g, '-');
        if (!headingLine.has(slug)) headingLine.set(slug, i);
      }
    });
    bodyLines.forEach((line, i) => {
      const re = /\]\(#([a-z0-9-]+)\)([^.\n]{0,40}?)\b(above|below)\b/gi;
      let m;
      while ((m = re.exec(line)) !== null) {
        const target = headingLine.get(m[1]);
        if (target === undefined) continue;
        const saidAbove = m[3].toLowerCase() === 'above';
        const isAbove = target < i;
        if (saidAbove !== isAbove) {
          log(
            'warning',
            filePath,
            `Line ${i + frontmatterEnd + 2}: says "${m[3]}" of #${m[1]}, which is ${isAbove ? 'above' : 'below'} it. Reordering breaks these silently; mkdocs --strict cannot see it because the anchor still resolves.`
          );
        }
      }
    });
  }

  // Check 17: the provenance fields -- date_created, date_modified, ai_provider_models -- on the
  // hand-written pages. They are written by utils/refresh_frontmatter_provenance.py from git
  // history; this check exists because a date typed into frontmatter goes stale the moment
  // someone edits the file and forgets, and a stale provenance record is worse than none.
  //
  // Scoped to hand-written pages: the commentary cross-reference pages are generated on demand by
  // commentary_index.py and carry its marker, and a provenance record on those would describe a
  // script run rather than authorship. Warnings, not errors, in the spirit of checks 10-16 --
  // the fix is always the same one command, and a stale date should never block a build.
  if (!content.includes('<!-- commentary-index:auto-start -->')) {
    for (const field of ['date_created', 'date_modified', 'ai_provider_models']) {
      if (!frontmatter.match(new RegExp(`^${field}:`, 'm'))) {
        log(
          'warning',
          filePath,
          `Missing "${field}" in frontmatter. Run \`python3 utils/refresh_frontmatter_provenance.py\` to fill the provenance fields in from git history.`
        );
      }
    }

    const modifiedMatch = frontmatter.match(/^date_modified:\s*(\d{4}-\d{2}-\d{2})\s*$/m);
    const lastCommit = LAST_COMMIT_DATES.get(path.relative(REPO_ROOT, filePath));
    if (modifiedMatch && lastCommit && modifiedMatch[1] < lastCommit) {
      log(
        'warning',
        filePath,
        `date_modified is ${modifiedMatch[1]} but the file was last committed ${lastCommit}. Run \`python3 utils/refresh_frontmatter_provenance.py\` to bring the provenance fields back in line with git.`
      );
    }

    // A model that isn't provider-qualified ("Claude Opus 5" rather than
    // "anthropic/claude-opus-5") reads fine to a human and sorts and greps badly.
    const modelsBlock = frontmatter.match(/^ai_provider_models:(.*(?:\n {2}-.*)*)/m);
    if (modelsBlock) {
      for (const entry of modelsBlock[1].matchAll(/(?:^|[[,\n])\s*-?\s*["']?([^,\]\n"']+)/g)) {
        const value = entry[1].trim();
        if (value && value !== '[]' && !value.includes('/')) {
          log(
            'warning',
            filePath,
            `ai_provider_models entry "${value}" is not provider-qualified. Use the "provider/model" form, e.g. anthropic/claude-opus-5.`
          );
        }
      }
    }
  }
}

function walkDirectory(dir) {
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      walkDirectory(fullPath);
    } else if (file.endsWith('.md')) {
      validateFile(fullPath);
    }
  }
}

console.log('🔍 Validating markdown content files...\n');

walkDirectory(CONTENT_DIR);

console.log('\n' + '='.repeat(50));
if (hasErrors) {
  console.error(`\n❌ Validation failed with errors`);
  console.log(`   Warnings: ${warningCount}`);
  process.exit(1);
} else if (warningCount > 0) {
  console.warn(`\n✅ Validation passed with ${warningCount} warning(s)`);
  process.exit(0);
} else {
  console.log(`\n✅ All content files are valid!`);
  process.exit(0);
}
