import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith('.md')) out.push(full);
  }
  return out;
}

export function generateEvents(contentDir, base) {
  return walk(contentDir)
    .map((file) => {
      const { data } = matter(fs.readFileSync(file, 'utf8'));
      if (data.zadok_year == null && data.gregorian_year == null) return null;
      const rel = path
        .relative(contentDir, file)
        .replace(/\\/g, '/')
        .replace(/\.md$/, '');
      return {
        slug: rel,
        title: data.title ?? 'Untitled Study',
        description: data.description ?? '',
        tags: data.tags ?? [],
        category: path.basename(path.dirname(rel)),
        zadok_year: data.zadok_year ?? null,
        gregorian_year: data.gregorian_year ?? null,
        url: `${base}/${rel}/`,
      };
    })
    .filter(Boolean)
    .sort((a, b) => (a.gregorian_year ?? 0) - (b.gregorian_year ?? 0));
}

const isMain = process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
  const contentDir = path.join(repoRoot, 'docs/content');
  const outFile = path.join(repoRoot, 'docs/data/events.json');
  const events = generateEvents(contentDir, '/bible_end_times');
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify(events, null, 2) + '\n');
  console.log(`Wrote ${events.length} events to ${outFile}`);
}
