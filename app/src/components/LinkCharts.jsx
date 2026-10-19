// The Scripture Links diagrams. Each is drawn from the same links the lookup shows, so they change
// when export_links.py is re-run and the site rebuilt, and a number in a diagram is a count of links
// a reader can open. Colours come from the CSS variables in tools.css (light and dark); each method
// also has its own line pattern, so nothing depends on telling two colours apart.
import { useMemo } from 'react';
import {
  METHODS,
  METHOD_NAMES,
  bookDegrees,
  bookFlows,
  displayBook as bookName,
  isNT,
  matrix,
  methodBreakdown,
  prettyKey,
  topTargets,
} from '../utils/scriptureLinks.js';

const ink = 'var(--color-text, #1a1a1a)';
const muted = 'var(--color-text-muted, #666)';
const line = 'var(--color-border, #ddd)';
const panel = 'var(--color-card-bg, #fafafa)';
const accent = 'var(--color-primary, #7a5c2e)';

const methodOf = (m) => METHODS[m] ?? { color: muted, dash: null, width: 1.5, label: m };
const nameOf = (m) => METHOD_NAMES[m] ?? methodOf(m).label;

export function MethodKey({ methods }) {
  return (
    <ul style={{ listStyle: 'none', padding: 0, margin: '0.6rem 0', display: 'flex', flexWrap: 'wrap', gap: '0.4rem 1.2rem', fontSize: '0.85rem' }}>
      {methods.map((m) => (
        <li key={m} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <svg width="34" height="8" aria-hidden="true">
            <line x1="1" x2="33" y1="4" y2="4" stroke={methodOf(m).color} strokeWidth={methodOf(m).width + 1} strokeDasharray={methodOf(m).dash ?? undefined} strokeLinecap="round" />
          </svg>
          {nameOf(m)}
        </li>
      ))}
    </ul>
  );
}

const polar = (cx, cy, r, deg) => {
  const a = ((deg - 90) * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
};

// The books round a ring in canonical order, Old Testament then New. A curve joins two books where a
// verse in one quotes or echoes a verse in the other, as wide as the number of such verses.
export function ChordMap({ links, active, setActive }) {
  const SIZE = 720;
  const C = SIZE / 2;
  const R = 262;
  const geo = useMemo(() => {
    const books = bookDegrees(links);
    const flows = bookFlows(links);
    const GAP = 0.9;
    const SPLIT = 5;
    const weight = (b) => b.n + 3;
    const sum = books.reduce((s, b) => s + weight(b), 0);
    const split = books.some((b) => isNT(b.book)) && books.some((b) => !isNT(b.book)) ? SPLIT : 0;
    const unit = (360 - books.length * GAP - split) / sum;
    const at = new Map();
    let angle = 0;
    books.forEach((b, i) => {
      if (i > 0 && isNT(b.book) && !isNT(books[i - 1].book)) angle += split;
      const span = weight(b) * unit;
      at.set(b.book, { i, a0: angle, a1: angle + span, mid: angle + span / 2, n: b.n, span });
      angle += span + GAP;
    });
    // At each book, order the curves so those bound for the far side of the ring nest outside those
    // bound for its neighbours: the curves then cross as little as they can.
    const ends = new Map();
    for (const f of flows) {
      for (const [self, other] of [[f.from, f.to], [f.to, f.from]]) {
        if (!ends.has(self)) ends.set(self, []);
        ends.get(self).push({ flow: f, other, count: f.links.length, self: f.from === f.to });
      }
    }
    const slots = new Map();
    for (const [book, list] of ends) {
      const here = at.get(book);
      const N = books.length;
      list.sort((p, q) => ((at.get(q.other).i - here.i + N) % N) - ((at.get(p.other).i - here.i + N) % N));
      const total = list.reduce((s, e) => s + e.count, 0);
      const inner = here.span * 0.94;
      let cursor = here.a0 + (here.span - inner) / 2;
      for (const e of list) {
        const w = (e.count / total) * inner;
        const key = `${e.flow.from}>${e.flow.to}>${e.flow.m}`;
        const end = slots.has(`${key}@${book}@0`) ? 1 : 0;
        slots.set(`${key}@${book}@${end}`, { a: cursor + w / 2, w });
        cursor += w;
      }
    }
    return { books, flows, at, slots };
  }, [links]);

  const isOn = (flow) => !active || active.book === flow.from || active.book === flow.to || (active.from === flow.from && active.to === flow.to);
  const bookOn = (book) => !active || active.book === book || active.from === book || active.to === book
    || geo.flows.some((f) => (f.from === active.book && f.to === book) || (f.to === active.book && f.from === book));

  const curves = geo.flows.map((f) => {
    const key = `${f.from}>${f.to}>${f.m}`;
    const s1 = geo.slots.get(`${key}@${f.from}@0`);
    const s2 = geo.slots.get(`${key}@${f.to}@${f.from === f.to ? 1 : 0}`) ?? s1;
    const [x1, y1] = polar(C, C, R - 3, s1.a);
    const [x2, y2] = polar(C, C, R - 3, s2.a);
    const pull = f.from === f.to ? 0.55 : 0.2;
    const mx = (x1 + x2) / 2;
    const my = (y1 + y2) / 2;
    const cx = C + (mx - C) * pull;
    const cy = C + (my - C) * pull;
    const arcLen = ((s1.w + s2.w) / 2) * (Math.PI / 180) * (R - 3);
    return { f, d: `M${x1} ${y1} Q${cx} ${cy} ${x2} ${y2}`, width: Math.max(1, Math.min(7, arcLen * 0.5)), id: key };
  }).sort((p, q) => q.width - p.width);

  return (
    <figure style={{ margin: 0 }}>
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} role="group" aria-label="Chord diagram of the books of the Bible, joined where one quotes or echoes another" style={{ width: '100%', maxWidth: '46rem', display: 'block', margin: '0 auto' }}>
        <g fill="none" strokeLinecap="round">
          {curves.map((c) => {
            const on = isOn(c.f);
            const meth = methodOf(c.f.m);
            return (
              <path
                key={c.id}
                d={c.d}
                stroke={meth.color}
                strokeWidth={c.width}
                strokeDasharray={meth.dash ?? undefined}
                opacity={on ? (active ? 0.85 : 0.42) : 0.05}
                style={{ cursor: 'pointer', transition: 'opacity .15s' }}
                onClick={() => setActive(active?.from === c.f.from && active?.to === c.f.to ? null : { from: c.f.from, to: c.f.to })}
              >
                <title>{`${bookName(c.f.from)} to ${bookName(c.f.to)}: ${c.f.links.length} ${nameOf(c.f.m).toLowerCase()} link${c.f.links.length === 1 ? '' : 's'}`}</title>
              </path>
            );
          })}
        </g>
        {geo.books.map(({ book, n }) => {
          const g = geo.at.get(book);
          const [sx, sy] = polar(C, C, R, g.a0);
          const [ex, ey] = polar(C, C, R, g.a1);
          const [ox, oy] = polar(C, C, R + 11, g.a0);
          const [px, py] = polar(C, C, R + 11, g.a1);
          const large = g.a1 - g.a0 > 180 ? 1 : 0;
          const [lx, ly] = polar(C, C, R + 16, g.mid);
          const flip = g.mid > 180;
          const on = bookOn(book);
          const isActive = active?.book === book;
          return (
            <g
              key={book}
              tabIndex={0}
              role="button"
              aria-pressed={isActive}
              aria-label={`${bookName(book)}, ${n} link${n === 1 ? '' : 's'}`}
              onClick={() => setActive(isActive ? null : { book })}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setActive(isActive ? null : { book }); } }}
              style={{ cursor: 'pointer', outline: 'none' }}
              opacity={on ? 1 : 0.35}
            >
              <path
                d={`M${sx} ${sy} A${R} ${R} 0 ${large} 1 ${ex} ${ey} L${px} ${py} A${R + 11} ${R + 11} 0 ${large} 0 ${ox} ${oy} Z`}
                fill={isNT(book) ? accent : 'var(--color-border-strong, #999)'}
                stroke={isActive ? ink : 'none'}
                strokeWidth="1.5"
              />
              <text
                x={lx}
                y={ly}
                fontSize="10.5"
                fill={ink}
                fontWeight={isActive ? 700 : 400}
                textAnchor={flip ? 'end' : 'start'}
                dominantBaseline="middle"
                transform={`rotate(${flip ? g.mid + 90 : g.mid - 90} ${lx} ${ly})`}
              >
                {bookName(book)}
              </text>
              <title>{`${bookName(book)}: ${n} link${n === 1 ? '' : 's'}`}</title>
            </g>
          );
        })}
      </svg>
      <figcaption style={{ fontSize: '0.85rem', color: muted, textAlign: 'center' }}>
        {links.length} links across {geo.books.length} books. Old Testament in grey, New Testament in the site colour, the Septuagint's extra books between. Select a book or a curve to list its links.
      </figcaption>
    </figure>
  );
}

// Every pair of books as a real table: a row is the book whose verses quote, a column the book
// quoted. The shading is a count, and the button in a cell lists those links.
export function MatrixTable({ links, active, setActive }) {
  const { rows, cols, cells } = useMemo(() => matrix(links), [links]);
  const max = useMemo(() => Math.max(1, ...[...cells.values()].map((c) => c.length)), [cells]);
  const rowTotal = (r) => cols.reduce((s, c) => s + (cells.get(`${r}>${c}`)?.length ?? 0), 0);
  const cell = { padding: 0, border: `1px solid ${line}`, textAlign: 'center', minWidth: '1.9rem', height: '1.9rem' };
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ borderCollapse: 'collapse', fontSize: '0.78rem', margin: '0 auto' }}>
        <caption style={{ captionSide: 'bottom', fontSize: '0.85rem', color: muted, padding: '0.5rem' }}>
          Rows are the books whose verses quote or echo; columns are the books they draw on.
        </caption>
        <thead>
          <tr>
            <th scope="col" style={{ ...cell, border: 'none' }}><span style={{ position: 'absolute', left: '-9999px' }}>Book</span></th>
            {cols.map((c) => (
              <th key={c} scope="col" style={{ ...cell, border: 'none', height: '6.2rem', verticalAlign: 'bottom', fontWeight: 600 }}>
                <span style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)', whiteSpace: 'nowrap', padding: '0.2rem 0' }}>{bookName(c)}</span>
              </th>
            ))}
            <th scope="col" style={{ ...cell, border: 'none', verticalAlign: 'bottom', color: muted }}>Total</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r}>
              <th scope="row" style={{ ...cell, border: 'none', textAlign: 'right', paddingRight: '0.5rem', whiteSpace: 'nowrap', fontWeight: 600 }}>{bookName(r)}</th>
              {cols.map((c) => {
                const here = cells.get(`${r}>${c}`);
                const on = active?.from === r && active?.to === c;
                return (
                  <td key={c} style={{ ...cell, background: here ? `color-mix(in srgb, ${accent} ${Math.round(15 + 80 * Math.sqrt(here.length / max))}%, transparent)` : 'transparent', outline: on ? `2px solid ${ink}` : 'none' }}>
                    {here && (
                      <button
                        type="button"
                        onClick={() => setActive(on ? null : { from: r, to: c })}
                        aria-label={`${bookName(r)} to ${bookName(c)}: ${here.length} link${here.length === 1 ? '' : 's'}`}
                        style={{ width: '100%', height: '100%', border: 0, background: 'transparent', color: ink, cursor: 'pointer', font: 'inherit' }}
                      >
                        {here.length}
                      </button>
                    )}
                  </td>
                );
              })}
              <td style={{ ...cell, border: 'none', color: muted }}>{rowTotal(r)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// How the links divide by the kind of evidence, and how many of each no reference list carries.
export function MethodBars({ links, methodOrder }) {
  const rows = useMemo(() => methodBreakdown(links, methodOrder).filter((r) => r.total > 0), [links, methodOrder]);
  const max = Math.max(1, ...rows.map((r) => r.total));
  return (
    <div>
      {rows.map((r) => {
        const meth = methodOf(r.m);
        return (
          <div key={r.m} style={{ margin: '0.7rem 0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', gap: '1rem', flexWrap: 'wrap' }}>
              <strong>{nameOf(r.m)}</strong>
              <span style={{ color: muted }}>{r.total} links · {r.found} found by the texts alone</span>
            </div>
            <svg viewBox="0 0 600 22" role="img" aria-label={`${nameOf(r.m)}: ${r.listed} also in reference lists, ${r.found} in none`} style={{ width: '100%', display: 'block' }}>
              <defs>
                <pattern id={`found-${r.m}`} width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                  <rect width="5" height="5" fill={meth.color} opacity="0.28" />
                  <line x1="0" y1="0" x2="0" y2="5" stroke={meth.color} strokeWidth="2.4" />
                </pattern>
              </defs>
              <rect x="0" y="2" width={(r.listed / max) * 600} height="18" fill={meth.color} />
              <rect x={(r.listed / max) * 600} y="2" width={(r.found / max) * 600} height="18" fill={`url(#found-${r.m})`} stroke={meth.color} strokeWidth="1" />
            </svg>
          </div>
        );
      })}
      <p style={{ fontSize: '0.85rem', color: muted, margin: '0.4rem 0 0' }}>
        Solid: the link is also in a conventional cross-reference list. Hatched: no reference list carries it, the connections this method exists to find.
      </p>
    </div>
  );
}

// The verses the rest of Scripture comes back to most.
export function TopVerses({ links, onOpen, n = 10 }) {
  const top = useMemo(() => topTargets(links, n), [links, n]);
  const max = Math.max(1, ...top.map((t) => t.total));
  return (
    <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {top.map((t) => (
        <li key={t.key} style={{ margin: '0.25rem 0' }}>
          <button
            type="button"
            onClick={() => onOpen(t.key)}
            style={{ display: 'grid', gridTemplateColumns: '8.5rem 1fr 2rem', alignItems: 'center', gap: '0.6rem', width: '100%', border: 0, background: 'transparent', color: ink, cursor: 'pointer', font: 'inherit', textAlign: 'left', padding: '0.15rem 0' }}
            aria-label={`${prettyKey(t.key)}, linked from ${t.total} verses. Open it.`}
          >
            <span>{prettyKey(t.key)}</span>
            <svg viewBox="0 0 300 12" aria-hidden="true" style={{ width: '100%' }}>
              <rect x="0" y="1" width={(t.total / max) * 300} height="10" rx="2" fill={accent} />
            </svg>
            <span style={{ color: muted, textAlign: 'right' }}>{t.total}</span>
          </button>
        </li>
      ))}
    </ol>
  );
}

const NODE_W = 196;
const NODE_H = 22;
const ROW_H = 28;
const MAX_NODES = 9;

// One verse and its neighbours: the verses that quote or echo it on the left, the verses it quotes
// or echoes on the right, every arrow running left to right. Selecting a node moves the lookup there.
export function EgoGraph({ label, entries, onOpen }) {
  const { incoming, outgoing } = useMemo(() => {
    const pick = (dir) => {
      const seen = new Map();
      for (const e of entries) {
        if (e.direction !== dir) continue;
        const other = dir === 'to' ? e.link.f : e.link.t;
        const id = `${other}|${e.link.m}`;
        if (!seen.has(id)) seen.set(id, { other, m: e.link.m, s: e.link.s, te: dir === 'from' ? e.link.te : null });
      }
      return [...seen.values()].sort((a, b) => b.s - a.s);
    };
    return { incoming: pick('to'), outgoing: pick('from') };
  }, [entries]);
  if (!incoming.length && !outgoing.length) return null;

  const rows = Math.max(Math.min(incoming.length, MAX_NODES), Math.min(outgoing.length, MAX_NODES), 1);
  const H = rows * ROW_H + 52;
  const W = 640;
  const midY = 40 + (rows * ROW_H) / 2;
  const cx0 = (W - 150) / 2;
  const column = (list, side) => list.slice(0, MAX_NODES).map((n, i) => {
    const y = 40 + i * ROW_H + (ROW_H - NODE_H) / 2;
    const meth = methodOf(n.m);
    const x = side === 'left' ? 4 : W - NODE_W - 4;
    const [x1, y1, x2, y2] = side === 'left' ? [x + NODE_W, y + NODE_H / 2, cx0, midY] : [cx0 + 150, midY, x, y + NODE_H / 2];
    const bend = (x2 - x1) / 2;
    return (
      <g key={`${side}-${n.other}-${n.m}`}>
        <path d={`M${x1} ${y1} C${x1 + bend} ${y1} ${x2 - bend} ${y2} ${x2 - 5} ${y2}`} fill="none" stroke={meth.color} strokeWidth={meth.width} strokeDasharray={meth.dash ?? undefined} />
        <polygon points={`${x2},${y2} ${x2 - 7},${y2 - 3.5} ${x2 - 7},${y2 + 3.5}`} fill={meth.color} />
        <g
          tabIndex={0}
          role="button"
          aria-label={`${prettyKey(n.other)}, ${nameOf(n.m).toLowerCase()}. Open it.`}
          onClick={() => onOpen(n.other)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(n.other); } }}
          style={{ cursor: 'pointer' }}
        >
          <rect x={x} y={y} width={NODE_W} height={NODE_H} rx={NODE_H / 2} fill={panel} stroke={meth.color} strokeWidth="1.6" strokeDasharray={meth.dash ?? undefined} />
          <text x={x + NODE_W / 2} y={y + NODE_H / 2 + 0.5} textAnchor="middle" dominantBaseline="middle" fontSize="12" fill={ink}>{n.te ? `${prettyKey(n.other)} (${prettyKey(n.te)})` : prettyKey(n.other)}</text>
          <title>{`${prettyKey(n.other)}: ${nameOf(n.m)}`}</title>
        </g>
      </g>
    );
  });

  return (
    <figure style={{ margin: '1rem 0' }}>
      <svg viewBox={`0 0 ${W} ${H}`} role="group" aria-label={`Verses that quote or echo ${label}, and verses it quotes or echoes`} style={{ width: '100%', maxWidth: '44rem', display: 'block' }}>
        <text x="4" y="22" fontSize="11" fill={muted}>{incoming.length ? 'Quoted or echoed by' : ''}</text>
        <text x={W - 4} y="22" fontSize="11" fill={muted} textAnchor="end">{outgoing.length ? 'Quotes or echoes' : ''}</text>
        {column(incoming, 'left')}
        {column(outgoing, 'right')}
        <rect x={cx0} y={midY - 15} width="150" height="30" rx="6" fill={accent} />
        <text x={cx0 + 75} y={midY + 0.5} textAnchor="middle" dominantBaseline="middle" fontSize="13" fontWeight="700" fill="var(--md-primary-bg-color, #fff)">{label}</text>
        {incoming.length > MAX_NODES && <text x="4" y={H - 6} fontSize="11" fill={muted}>{`+${incoming.length - MAX_NODES} more below`}</text>}
        {outgoing.length > MAX_NODES && <text x={W - 4} y={H - 6} fontSize="11" fill={muted} textAnchor="end">{`+${outgoing.length - MAX_NODES} more below`}</text>}
      </svg>
    </figure>
  );
}
