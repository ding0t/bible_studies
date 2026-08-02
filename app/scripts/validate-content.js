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
