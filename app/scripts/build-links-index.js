// Which verses have scripture links, and how many each way, for the verse pop-ups. Derived from
// docs/data/scripture-links.json on every build so the pop-up never offers a link the Scripture
// Links page cannot answer. Keyed as that file is: "Heb 10:5" (Psalms in the Septuagint's numbering,
// with the English number alongside).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

export function linkIndex(links) {
  const out = {};
  const bump = (key, slot) => {
    out[key] ??= [0, 0];
    out[key][slot] += 1;
  };
  for (const l of links) {
    bump(l.f, 0);
    bump(l.t, 1);
    if (l.te && l.te !== l.t) bump(l.te, 1);
  }
  return out;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const data = JSON.parse(fs.readFileSync(path.join(root, 'docs/data/scripture-links.json'), 'utf8'));
  const index = linkIndex(data.links);
  const dest = path.join(root, 'docs/content/assets/popups/links.json');
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, JSON.stringify(index));
  console.log(`wrote ${path.relative(root, dest)}: ${Object.keys(index).length} verses`);
}
