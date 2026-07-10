/**
 * contentTree.js
 * Central utility for directory-driven site structure.
 * Derives navigation, labels, colors, and URLs from docs/content/ file paths.
 */

// import.meta.glob must be at module scope — Vite resolves it at build time.
// Keys will be like: /docs/content/studies/_category.json
const categoryMeta = import.meta.glob('/docs/content/**/_category.json', { eager: true });

const COLOR_PALETTE = [
  '#3b82f6', // blue
  '#10b981', // emerald
  '#8b5cf6', // violet
  '#f59e0b', // amber
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#ef4444', // red
  '#84cc16', // lime
  '#f97316', // orange
  '#6366f1', // indigo
  '#14b8a6', // teal
  '#a855f7', // purple
];

/**
 * Auto-derive a human-readable label from a directory name.
 * "spiritual-disciplines" → "Spiritual Disciplines"
 * "hebrew-studies"       → "Hebrew Studies"
 */
export function getDirLabel(dirName) {
  return dirName
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

/**
 * Deterministic color assignment from a string via simple hash.
 * Same dir name always gets the same color.
 */
function hashColor(str) {
  let h = 0;
  for (const c of str) h = ((h << 5) - h + c.charCodeAt(0)) | 0;
  return COLOR_PALETTE[Math.abs(h) % COLOR_PALETTE.length];
}

/**
 * Get metadata for a directory path, merging _category.json (if present)
 * over auto-derived defaults.
 *
 * @param {string} dirPath - Relative path from docs/content, e.g. "studies" or "studies/spiritual-disciplines"
 * @returns {{ label: string, color: string, icon: string|null, order: number }}
 */
export function getDirMeta(dirPath) {
  const key = `/docs/content/${dirPath}/_category.json`;
  const override = categoryMeta[key];
  const dirName = dirPath.split('/').pop();
  const defaults = {
    label: getDirLabel(dirName),
    color: hashColor(dirName),
    icon: null,
    order: 999,
  };
  if (!override) return defaults;
  // Vite eager imports expose the JSON as the module default or directly
  const data = override.default ?? override;
  return { ...defaults, ...data };
}

/**
 * Compute the canonical URL for a content entry.
 * entry.id is the path relative to docs/content, e.g. "studies/spiritual-disciplines/prayer.md"
 * URL = "/" + id with .md stripped
 */
export function getEntryUrl(entry) {
  return '/' + entry.id.replace(/\.md$/, '');
}

/**
 * Get the Level-1 section name (first path segment).
 * "studies/spiritual-disciplines/prayer.md" → "studies"
 */
export function getEntrySection(entry) {
  return entry.id.split('/')[0];
}

/**
 * Get the Level-2 subsection name (second path segment) if the entry
 * lives inside a subsection directory, otherwise null.
 * "studies/spiritual-disciplines/prayer.md" → "spiritual-disciplines"
 * "sermons/as-the-snake-was-lifted.md"      → null
 */
export function getEntrySubsection(entry) {
  const parts = entry.id.split('/');
  return parts.length >= 3 ? parts[1] : null;
}

/**
 * Build the full content tree from a flat array of collection entries.
 *
 * Returns a tree object:
 * {
 *   [sectionDir]: {
 *     meta: { label, color, icon, order },
 *     files: [entry, ...],           // entries directly in this section
 *     subsections: {
 *       [subsectionDir]: {
 *         meta: { label, color, icon, order },
 *         files: [entry, ...]        // entries in this subsection
 *       }
 *     }
 *   }
 * }
 *
 * Files are sorted by title within each bucket.
 *
 * @param {Array} entries - Collection entries, already filtered for draft/title
 * @returns {Object} tree
 */
export function buildContentTree(entries) {
  const tree = {};

  for (const entry of entries) {
    const parts = entry.id.split('/');
    const section = parts[0];
    const subsection = parts.length >= 3 ? parts[1] : null;

    if (!tree[section]) {
      tree[section] = {
        meta: getDirMeta(section),
        files: [],
        subsections: {},
      };
    }

    if (subsection) {
      if (!tree[section].subsections[subsection]) {
        tree[section].subsections[subsection] = {
          meta: getDirMeta(`${section}/${subsection}`),
          files: [],
        };
      }
      tree[section].subsections[subsection].files.push(entry);
    } else {
      tree[section].files.push(entry);
    }
  }

  // Sort files within each bucket by title
  const byTitle = (a, b) => (a.data.title || '').localeCompare(b.data.title || '');
  for (const section of Object.values(tree)) {
    section.files.sort(byTitle);
    for (const sub of Object.values(section.subsections)) {
      sub.files.sort(byTitle);
    }
  }

  return tree;
}

/**
 * Get section entries sorted by order (from _category.json) then label.
 * @param {Object} tree - from buildContentTree
 * @returns {Array<[string, object]>} sorted [key, node] pairs
 */
export function getSortedSections(tree) {
  return Object.entries(tree).sort(([, a], [, b]) => {
    if (a.meta.order !== b.meta.order) return a.meta.order - b.meta.order;
    return a.meta.label.localeCompare(b.meta.label);
  });
}

/**
 * Get subsection entries for a section node, sorted by order then label.
 * @param {Object} sectionNode
 * @returns {Array<[string, object]>} sorted [key, node] pairs
 */
export function getSortedSubsections(sectionNode) {
  return Object.entries(sectionNode.subsections).sort(([, a], [, b]) => {
    if (a.meta.order !== b.meta.order) return a.meta.order - b.meta.order;
    return a.meta.label.localeCompare(b.meta.label);
  });
}
