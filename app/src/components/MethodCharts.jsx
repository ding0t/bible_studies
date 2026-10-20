// The method's own evidence, drawn: how often each rule is confirmed, what it finds that no other
// rule does, where the rules agree, and what all of them miss. Everything numeric comes from
// docs/data/link-method.json, which export_links.py writes from the database, so these charts follow
// every rebuild of the links. What each rule sees, and the cases shown for its strength and its
// weakness, are editorial and live in RULES (scriptureLinks.js).
import { useMemo, useState } from 'react';
import { METHODS, RULES, ruleById, prettyKey } from '../utils/scriptureLinks.js';

const ink = 'var(--color-text, #1a1a1a)';
const muted = 'var(--color-text-muted, #666)';
const line = 'var(--color-border, #ddd)';
const panel = 'var(--color-card-bg, #fafafa)';
const accent = 'var(--color-primary, #7a5c2e)';

const NT_RULES = RULES.filter((r) => r.method !== 'inner-biblical');
const OT_RULES = RULES.filter((r) => r.method === 'inner-biblical');
const colourOf = (id) => METHODS[ruleById[id]?.method]?.color ?? muted;
const pct = (n, d) => (d ? Math.round((100 * n) / d) : 0);

function Swatch({ id, width = 30 }) {
  const r = ruleById[id];
  return (
    <svg width={width} height="10" aria-hidden="true" style={{ flex: 'none' }}>
      <line x1="2" x2={width - 2} y1="5" y2="5" stroke={colourOf(id)} strokeWidth="3" strokeDasharray={r?.dash ?? undefined} strokeLinecap="round" />
    </svg>
  );
}

// A rule's share of a key, as a fill pattern: solid, striped or dotted by its dash, so the waffle
// and the agreement bars stay readable without colour.
function Patterns({ rules }) {
  return (
    <defs>
      {rules.map((r) => (
        <pattern key={r.id} id={`fill-${r.id}`} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform={r.dash === '5 3' ? 'rotate(45)' : undefined}>
          <rect width="6" height="6" fill={colourOf(r.id)} opacity={r.dash ? 0.35 : 1} />
          {r.dash === '5 3' && <line x1="0" y1="0" x2="0" y2="6" stroke={colourOf(r.id)} strokeWidth="3" />}
          {r.dash && r.dash !== '5 3' && <circle cx="3" cy="3" r="1.7" fill={colourOf(r.id)} />}
        </pattern>
      ))}
    </defs>
  );
}

// Confirmation against Greek alignment for every pair the method scores, strong or not, with the
// line the cut-off sits on and the rate two random verses achieve.
export function ConfirmationCurve({ method }) {
  const W = 640;
  const H = 230;
  const L = 40;
  const B = 44;
  const bins = method.curve;
  const bw = (W - L - 10) / bins.length;
  const y = (rate) => H - B - rate * (H - B - 14);
  const cut = bins.findIndex((b) => b.from >= method.threshold);
  return (
    <div style={{ margin: '1rem 0' }}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Share of Greek pairs confirmed by an outside list at each alignment score; the strong line is ${method.threshold}.`} style={{ width: '100%', display: 'block' }}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <g key={t}>
            <line x1={L} x2={W - 10} y1={y(t)} y2={y(t)} stroke={line} />
            <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill={muted}>{t * 100}%</text>
          </g>
        ))}
        <rect x={L + cut * bw} y={8} width={W - 10 - L - cut * bw} height={H - B - 8} fill={METHODS['quotation-greek'].color} opacity="0.07" />
        {bins.map((b, i) => {
          const rate = b.confirmed / b.pairs;
          const strong = b.from >= method.threshold;
          return (
            <g key={b.from}>
              <title>{`Alignment ${b.from}${b.from >= 40 ? '+' : `–${b.from + 1}`}: ${b.confirmed} of ${b.pairs} confirmed (${pct(b.confirmed, b.pairs)}%)`}</title>
              <rect x={L + i * bw + 2} y={y(rate)} width={bw - 4} height={H - B - y(rate)} fill={strong ? METHODS['quotation-greek'].color : muted} opacity={strong ? 0.9 : 0.45} rx="2" />
              <text x={L + i * bw + bw / 2} y={H - B + 14} textAnchor="middle" fontSize="10" fill={muted}>{b.from >= 40 ? '40+' : b.from}</text>
              <text x={L + i * bw + bw / 2} y={H - B + 27} textAnchor="middle" fontSize="9" fill={muted}>{b.pairs.toLocaleString()}</text>
            </g>
          );
        })}
        <line x1={L + cut * bw} x2={L + cut * bw} y1={8} y2={H - B} stroke={ink} strokeWidth="1.5" strokeDasharray="4 3" />
        <text x={L + cut * bw + 5} y={20} fontSize="11" fill={ink}>strong from {method.threshold}</text>
        <line x1={L} x2={W - 10} y1={y(method.baseline)} y2={y(method.baseline)} stroke={accent} strokeWidth="1.5" />
        <line x1={L + 8} x2={L + 26} y1={18} y2={18} stroke={accent} strokeWidth="1.5" />
        <text x={L + 30} y={22} fontSize="11" fill={accent}>two random verses: {(100 * method.baseline).toFixed(2)}%</text>
        <text x={L} y={H - 4} fontSize="10" fill={muted}>alignment score · pairs scored</text>
      </svg>
    </div>
  );
}

// Trust against contribution: across, how often a rule's links are confirmed; up, how many answer-key
// quotations that rule alone finds, which is what the method would lose without it. Labels sit in a
// column at the right with leader lines, so clustered rules stay legible.
function TrustPanel({ method, rules, title, keyTotal, onFocus, focus }) {
  const W = 400;
  const H = 250;
  const L = 34;
  const R = 168;
  const T = 26;
  const B = 34;
  const pts = rules.map((r) => {
    const s = method.rules[r.id] ?? { links: 0, confirmed: 0 };
    return { r, rate: s.links ? s.confirmed / s.links : 0, alone: s.keyAlone ?? 0, links: s.links };
  });
  const maxY = Math.max(5, ...pts.map((p) => p.alone));
  const x = (rate) => L + rate * (W - L - R);
  const yv = (v) => H - B - (v / maxY) * (H - B - T);
  const labels = [...pts].sort((a, b) => yv(a.alone) - yv(b.alone));
  // Push labels apart downward, then back up from the axis if the last one fell below it.
  let last = -Infinity;
  for (const p of labels) {
    p.ly = Math.max(yv(p.alone), last + 15);
    last = p.ly;
  }
  let floor = H - B;
  for (const p of [...labels].reverse()) {
    p.ly = Math.min(p.ly, floor);
    floor = p.ly - 15;
  }
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="group" aria-label={title} style={{ width: '100%', display: 'block' }}>
      <text x={L} y={14} fontSize="12" fontWeight="600" fill={ink}>{title}</text>
      {[0, 0.5, 1].map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={T} y2={H - B} stroke={line} />
          <text x={x(t)} y={H - B + 13} textAnchor="middle" fontSize="10" fill={muted}>{t * 100}%</text>
        </g>
      ))}
      <line x1={L} x2={W - R} y1={H - B} y2={H - B} stroke={muted} />
      <text x={(L + W - R) / 2} y={H - 6} textAnchor="middle" fontSize="10" fill={muted}>confirmed by an outside list →</text>
      <text transform={`translate(11 ${(T + H - B) / 2}) rotate(-90)`} textAnchor="middle" fontSize="10" fill={muted}>
        found by this rule alone ↑
      </text>
      <text x={L + 2} y={yv(maxY) + 10} fontSize="9" fill={muted}>{maxY} of {keyTotal}</text>
      {pts.map((p) => {
        const on = !focus || focus === p.r.id;
        const r = 4 + Math.sqrt(p.links) / 3;
        return (
          <g key={p.r.id} opacity={on ? 1 : 0.3} onMouseEnter={() => onFocus(p.r.id)} onMouseLeave={() => onFocus(null)} style={{ cursor: 'default' }}>
            <title>{`${p.r.name}: ${p.links} links, ${pct(p.rate * 1000, 1000)}% confirmed, ${p.alone} answer-key quotations no other rule finds`}</title>
            <circle cx={x(p.rate)} cy={yv(p.alone)} r={r} fill={colourOf(p.r.id)} fillOpacity="0.25" stroke={colourOf(p.r.id)} strokeWidth="2" strokeDasharray={p.r.dash ?? undefined} />
            <line x1={x(p.rate) + r} y1={yv(p.alone)} x2={W - R + 6} y2={p.ly} stroke={colourOf(p.r.id)} strokeOpacity="0.5" />
            <text x={W - R + 9} y={p.ly + 4} fontSize="10.5" fill={ink}>{p.r.name}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function TrustMap({ method }) {
  const [focus, setFocus] = useState(null);
  return (
    <div style={{ margin: '1rem 0' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(17rem, 1fr))', gap: '1rem' }}>
        <TrustPanel method={method} rules={NT_RULES} keyTotal={method.key.total} title="The New Testament quoting the Old" onFocus={setFocus} focus={focus} />
        <TrustPanel method={method} rules={OT_RULES} keyTotal={method.otKey.total} title="The Old Testament quoting itself" onFocus={setFocus} focus={focus} />
      </div>
      <p style={{ fontSize: '0.85rem', color: muted, marginTop: '0.4rem' }}>
        Right is more trustworthy; higher adds more that nothing else finds. A circle’s size is the number of links the rule admits.
        The answer keys are the WEB translators’ quotation footnotes with unfoldingWord’s Translation Notes ({method.key.total} quotations), and
        sixteen well-known Old Testament parallels ({method.otKey.total} verses).
      </p>
    </div>
  );
}

function Gauge({ value, of, colour, label, mark }) {
  const share = of ? value / of : 0;
  return (
    <div style={{ margin: '0.3rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: muted, gap: '0.5rem' }}>
        <span>{label}</span>
        <span style={{ color: ink, fontVariantNumeric: 'tabular-nums' }}>{mark}</span>
      </div>
      <svg viewBox="0 0 200 8" preserveAspectRatio="none" aria-hidden="true" style={{ width: '100%', height: '8px', display: 'block' }}>
        <rect width="200" height="8" rx="4" fill={line} />
        <rect width={Math.max(share > 0 ? 3 : 0, share * 200)} height="8" rx="4" fill={colour} />
      </svg>
    </div>
  );
}

// One card per rule: what it sees, three live measures, and a case of its strength and of its
// weakness that opens in the lookup.
export function RuleProfiles({ method, onOpen, rules = RULES }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(16.5rem, 1fr))', gap: '0.8rem', margin: '1rem 0' }}>
      {rules.map((r) => {
        const s = method.rules[r.id] ?? { links: 0, confirmed: 0 };
        const key = r.method === 'inner-biblical' ? method.otKey : method.key;
        const colour = colourOf(r.id);
        const cite = (text, ref) => (ref ? (
          <>{text} <button type="button" onClick={() => onOpen(ref)} style={{ background: 'none', border: 0, padding: 0, color: accent, cursor: 'pointer', font: 'inherit', textDecoration: 'underline' }}>Open {prettyKey(ref)}</button></>
        ) : text);
        return (
          <article key={r.id} style={{ border: `1px solid ${line}`, borderTop: `4px solid ${colour}`, borderRadius: '6px', padding: '0.7rem 0.8rem', background: panel }}>
            <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.95rem' }}>
              <Swatch id={r.id} /> {r.name}
            </h4>
            <p style={{ margin: '0.35rem 0 0.5rem', fontSize: '0.85rem', color: muted }}>{r.sees}</p>
            <Gauge label="Confirmed by an outside list" value={s.confirmed} of={s.links} colour={colour} mark={`${pct(s.confirmed, s.links)}% of ${s.links.toLocaleString()}`} />
            <Gauge label="Links no other rule makes" value={s.alone ?? 0} of={s.links} colour={colour} mark={`${(s.alone ?? 0).toLocaleString()}`} />
            <Gauge label="Answer-key quotations only it finds" value={s.keyAlone ?? 0} of={key.total - key.missed.length} colour={colour} mark={`${s.keyAlone ?? 0} of ${key.total - key.missed.length} found`} />
            <p style={{ margin: '0.6rem 0 0.25rem', fontSize: '0.85rem' }}><strong style={{ color: colour }}>Strength.</strong> {cite(r.strong, r.strongRef)}</p>
            <p style={{ margin: 0, fontSize: '0.85rem' }}><strong style={{ color: muted }}>Weakness.</strong> {cite(r.weak, r.weakRef)}</p>
          </article>
        );
      })}
    </div>
  );
}

// Where the rules agree, in the manner of an UpSet plot: one column per combination of rules, the dots
// beneath naming the rules, the bar the connections they share, solid where an outside list confirms.
export function RuleAgreement({ method, scope = 'nt', n = 12 }) {
  const rules = scope === 'nt' ? NT_RULES : OT_RULES;
  const sets = (scope === 'nt' ? method.overlap : method.otOverlap).slice(0, n);
  const W = 640;
  const labelW = 170;
  const barH = 120;
  const rowH = 17;
  const colW = (W - labelW) / Math.max(sets.length, 1);
  const H = barH + 16 + rules.length * rowH + 6;
  const max = Math.max(...sets.map((s) => s.links));
  return (
    <div style={{ margin: '1rem 0', overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${W} ${H}`} role="group" aria-label="Combinations of rules that find the same connection" style={{ width: '100%', minWidth: '34rem', display: 'block' }}>
        <defs>
          <pattern id="agree-unconfirmed" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="5" stroke={muted} strokeWidth="1.6" />
          </pattern>
        </defs>
        {sets.map((s, i) => {
          const cx = labelW + i * colW + colW / 2;
          const h = (s.links / max) * (barH - 14);
          const hc = (s.confirmed / max) * (barH - 14);
          const lead = s.rules.length === 1 ? colourOf(s.rules[0]) : ink;
          const members = rules.map((r, j) => ({ j, on: s.rules.includes(r.id) })).filter((m) => m.on);
          return (
            <g key={s.rules.join('+')}>
              <title>{`${s.rules.map((id) => ruleById[id]?.name ?? id).join(' + ')}: ${s.links} connections, ${s.confirmed} confirmed`}</title>
              <rect x={cx - colW * 0.32} y={barH - h} width={colW * 0.64} height={h - hc} fill="url(#agree-unconfirmed)" stroke={lead} strokeWidth="1" />
              <rect x={cx - colW * 0.32} y={barH - hc} width={colW * 0.64} height={hc} fill={lead} />
              <text x={cx} y={barH - h - 3} textAnchor="middle" fontSize="10" fill={ink}>{s.links}</text>
              {members.length > 1 && (
                <line x1={cx} x2={cx} y1={barH + 16 + members[0].j * rowH + rowH / 2} y2={barH + 16 + members.at(-1).j * rowH + rowH / 2} stroke={ink} strokeWidth="2" />
              )}
              {rules.map((r, j) => (
                <circle key={r.id} cx={cx} cy={barH + 16 + j * rowH + rowH / 2} r="4.5" fill={s.rules.includes(r.id) ? colourOf(r.id) : line} />
              ))}
            </g>
          );
        })}
        {rules.map((r, j) => (
          <text key={r.id} x={labelW - 8} y={barH + 16 + j * rowH + rowH / 2 + 4} textAnchor="end" fontSize="11" fill={ink}>{r.name}</text>
        ))}
      </svg>
      <p style={{ fontSize: '0.85rem', color: muted }}>
        Each column is one combination of rules; the dots beneath say which. Solid: confirmed by an outside list. Striped: no list records it.
        A column with a single dot is what that rule contributes on its own.
      </p>
    </div>
  );
}

// The answer key as a waffle, one square per quotation the key names: filled by the rule that alone
// found it, dark where several did, hollow where none did. The hollow squares are the method's limit.
export function KeyCoverage({ method, scope = 'nt', onOpen }) {
  const key = scope === 'nt' ? method.key : method.otKey;
  const rules = scope === 'nt' ? NT_RULES : OT_RULES;
  const [showAll, setShowAll] = useState(false);
  const cells = useMemo(() => {
    const out = [];
    const single = key.foundBy.filter((f) => f.rules.length === 1);
    const several = key.foundBy.filter((f) => f.rules.length > 1).reduce((s, f) => s + f.n, 0);
    for (const r of rules) {
      const n = single.find((f) => f.rules[0] === r.id)?.n ?? 0;
      for (let i = 0; i < n; i += 1) out.push(`url(#fill-${r.id})`);
    }
    for (let i = 0; i < several; i += 1) out.push(ink);
    while (out.length < key.total) out.push(null);
    return { out, several };
  }, [key, rules]);
  const COLS = 30;
  const S = 13;
  const W = COLS * S;
  const rows = Math.ceil(key.total / COLS);
  const found = key.total - key.missed.length;
  return (
    <div style={{ margin: '1rem 0' }}>
      <svg viewBox={`0 0 ${W} ${rows * S}`} role="img" aria-label={`${found} of ${key.total} answer-key quotations found; ${key.missed.length} missed`} style={{ width: '100%', maxWidth: '40rem', display: 'block' }}>
        <Patterns rules={rules} />
        {cells.out.map((fill, i) => (
          <rect key={i} x={(i % COLS) * S + 1} y={Math.floor(i / COLS) * S + 1} width={S - 2} height={S - 2} rx="2"
            fill={fill ?? 'none'} stroke={fill ? 'none' : muted} strokeWidth="1" />
        ))}
      </svg>
      <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0', display: 'flex', flexWrap: 'wrap', gap: '0.3rem 1rem', fontSize: '0.82rem' }}>
        {rules.map((r) => {
          const n = key.foundBy.find((f) => f.rules.length === 1 && f.rules[0] === r.id)?.n ?? 0;
          return n > 0 && (
            <li key={r.id} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <svg width="12" height="12" aria-hidden="true"><Patterns rules={[r]} /><rect width="12" height="12" rx="2" fill={`url(#fill-${r.id})`} /></svg>
              {r.name} alone: {n}
            </li>
          );
        })}
        <li style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <svg width="12" height="12" aria-hidden="true"><rect width="12" height="12" rx="2" fill={ink} /></svg> several rules: {cells.several}
        </li>
        <li style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <svg width="12" height="12" aria-hidden="true"><rect x="0.5" y="0.5" width="11" height="11" rx="2" fill="none" stroke={muted} /></svg> missed: {key.missed.length}
        </li>
      </ul>
      <p style={{ fontSize: '0.85rem', color: muted }}>
        {found} of {key.total} found ({pct(found, key.total)}%).{' '}
        <button type="button" onClick={() => setShowAll((v) => !v)} style={{ background: 'none', border: 0, padding: 0, color: accent, cursor: 'pointer', font: 'inherit', textDecoration: 'underline' }}>
          {showAll ? 'Hide' : 'List'} the {key.missed.length} missed
        </button>
      </p>
      {showAll && (
        <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0', columns: '13rem auto', fontSize: '0.85rem' }}>
          {key.missed.map(([from, to]) => (
            <li key={`${from}>${to}`} style={{ breakInside: 'avoid' }}>
              <button type="button" onClick={() => onOpen(from)} style={{ background: 'none', border: 0, padding: 0, color: accent, cursor: 'pointer', font: 'inherit', textDecoration: 'underline' }}>{prettyKey(from)}</button>
              <span style={{ color: muted }}> → {prettyKey(to)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
