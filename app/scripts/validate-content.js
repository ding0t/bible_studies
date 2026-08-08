#!/usr/bin/env node

/**
 * Validates markdown content files for common issues
 * Run with: node scripts/validate-content.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONTENT_DIR = path.join(__dirname, '../../docs/content');

let hasErrors = false;
let warningCount = 0;

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
  // generic "it is/it's worth <anything>ing" that catches fillers nobody has thought of yet.
  // Listing only the known fillers would repeat the exact mistake this check exists to fix.
  const worthPattern = new RegExp(
    [
      String.raw`\bworth\s+(?:being\s+clear|noting|stating|saying|asking|making|pointing\s+out|flagging|remembering|mentioning|bearing\s+in\s+mind|a\s+mention|repeating|emphasi[sz]ing)\b`,
      String.raw`\bit(?:'s|’s|\s+is)\s+worth\s+\w+ing\b`,
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
