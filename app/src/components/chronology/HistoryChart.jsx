import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  CHRONOLOGY,
  amToGregorian,
  loadEvents,
  loadGenealogyPeople,
  mergePeopleWithVariant,
} from '../../utils/chronology';
import {
  SHEET,
  amTicks,
  formatYear,
  gregorianTicks,
  makeScale,
  packRows,
  peopleLevel,
  placeCallouts,
  presentAm,
  resolveAges,
  resolveMovements,
  resolvePeriods,
  resolveThreads,
  splitSheets,
  textWidth,
} from '../../utils/historyChart';
import DanielKingdoms from './DanielKingdoms';
import { CORE_ONLY_SPAN, chip, sectionLabel, studyUrl, theme } from './shared';

// The printable chart: the chronology as A4 sheets, drawn from the same events as the timeline.
// The sheet is paper whatever the site's palette, because it is a picture of what will print.
const SPRITES_URL = '/assets/chart/sprites.svg';
const PAGE_URL = 'the-way.lewy.au/timeline/';
const EPOCH = 'genealogy';
const SERIF = "Georgia, 'Times New Roman', serif";
const INK = '#3b2f1e';
const MUTED = '#6b5a3e';
const PAPER = '#faf6ec';
const RED = '#8b1e1e';

// Every age has a pattern as well as a tint, so a black-and-white print (or a photocopy of a colour
// one) still tells the ages apart.
const AGE_STYLE = {
  antediluvian: { tint: '#dde6f1', pattern: 'dots' },
  postdiluvian: { tint: '#e0ecd9', pattern: 'diag' },
  patriarchs: { tint: '#f3e6c4', pattern: 'horiz' },
  law: { tint: '#f1dcd4', pattern: 'cross' },
  church: { tint: '#e5def0', pattern: 'vert' },
  kingdom: { tint: '#f6ecd0', pattern: 'diag2' },
  new_creation: { tint: '#fbf8ee', pattern: null },
};
const THREAD_STYLE = {
  seed: { color: RED, dash: null },
  temple: { color: '#2f4f7f', dash: '2.2 1' },
  seventy_weeks: { color: '#a67c3d', dash: '0.7 0.9' },
};
const KIND_LABEL = {
  manuscript: 'Copy of Scripture',
  inscription: 'Inscription',
  historian: 'Ancient writer',
  archaeology: 'Dated record',
};

function readHash() {
  const out = {};
  for (const part of window.location.hash.replace(/^#/, '').split('&').filter(Boolean)) {
    const [k, v = ''] = part.split('=');
    out[k] = decodeURIComponent(v);
  }
  return out;
}

const LANES = [
  { id: 'scripture', label: 'Scripture and history' },
  { id: 'people', label: 'People' },
  { id: 'texts', label: 'Texts and finds' },
  { id: 'threads', label: 'Threads' },
  { id: 'pictures', label: 'Pictures' },
];

// The Chart view of the chronology page (ChronologyExplorer), which owns the period, the address bar
// and the detail panels; this component owns only what is particular to print. Events and people
// clicked on a sheet open the Timeline's own panels; the ages, periods, threads and kingdoms, which
// the Timeline has no panel for, open a card here.
const EVENT_SOURCES = new Set(['genesis', 'anchor', 'archaeology', 'artifact', 'milestone', 'life', 'passion']);

export default function HistoryChart({
  amStart,
  amEnd,
  title,
  slug,
  daniel,
  onSelectEvent,
  onSelectPerson,
  onOptionsChange,
}) {
  const hash = useMemo(() => readHash(), []);
  const [sheets, setSheets] = useState(Math.min(12, Math.max(1, Number(hash.sheets) || 1)));
  const [scaleMode, setScaleMode] = useState(hash.scale === 'even' ? 'even' : 'fitted');
  const [mono, setMono] = useState(hash.ink === 'mono');
  const [lanes, setLanes] = useState(
    Object.fromEntries(LANES.map((l) => [l.id, !(hash.off ?? '').split(',').includes(l.id)]))
  );
  const [sprite, setSprite] = useState('');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch(SPRITES_URL)
      .then((r) => (r.ok ? r.text() : ''))
      .then(setSprite)
      .catch(() => setSprite(''));
  }, []);

  useEffect(() => {
    const parts = [];
    if (sheets > 1) parts.push(`sheets=${sheets}`);
    if (scaleMode === 'even') parts.push('scale=even');
    if (mono) parts.push('ink=mono');
    const off = LANES.filter((l) => !lanes[l.id]).map((l) => l.id);
    if (off.length) parts.push(`off=${off.join(',')}`);
    onOptionsChange?.(parts);
  }, [sheets, scaleMode, mono, lanes, onOptionsChange]);

  const vignettes = useMemo(
    () => new Set([...sprite.matchAll(/<symbol id="v-([^"]+)"/g)].map((m) => m[1])),
    [sprite]
  );

  const data = useMemo(() => {
    const events = loadEvents();
    return {
      events,
      ages: resolveAges(events),
      periods: resolvePeriods(events),
      movements: resolveMovements(events),
      threads: resolveThreads(events),
      people: mergePeopleWithVariant(loadGenealogyPeople(), 'mt').filter(
        (p) => p.zadok_year_born != null && p.zadok_year_died != null
      ),
      now: presentAm(),
    };
  }, []);

  const ranges = splitSheets(amStart, amEnd, sheets);
  const byId = useMemo(() => new Map(data.events.map((e) => [e.id, e])), [data]);
  const select = (item) => {
    if (item.source === 'movement' && byId.has(item.event)) return onSelectEvent(byId.get(item.event));
    if (EVENT_SOURCES.has(item.source)) return onSelectEvent(item);
    if (item.zadok_year_born != null && item.id) return onSelectPerson(item.id);
    setSelected(item);
  };

  const card = {
    padding: '1rem 1.25rem',
    background: theme.cardBg,
    border: `1px solid ${theme.border}`,
    borderRadius: '0.75rem',
    marginBottom: '0.75rem',
  };
  const input = {
    width: '7rem',
    padding: '0.35rem 0.5rem',
    borderRadius: '0.4rem',
    border: `1px solid ${theme.border}`,
    background: theme.bgElevated,
    color: theme.text,
    fontSize: '0.8rem',
  };
  const row = { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' };

  return (
    <div className="hc-root" style={{ color: theme.text }}>
      <div dangerouslySetInnerHTML={{ __html: sprite }} />
      <div className="hc-controls" style={card}>
        <div style={sectionLabel}>SHOW</div>
        <div style={row}>
          {LANES.map((l) => (
            <button
              key={l.id}
              style={chip(lanes[l.id], '#0f766e')}
              onClick={() => setLanes((s) => ({ ...s, [l.id]: !s[l.id] }))}
            >
              {l.label}
            </button>
          ))}
        </div>
        <div style={sectionLabel}>PRINT</div>
        <div style={{ ...row, alignItems: 'center', marginBottom: 0 }}>
          <span style={{ fontSize: '0.8rem', color: theme.textMuted }}>Sheets</span>
          <select
            value={sheets}
            onChange={(e) => setSheets(Number(e.target.value))}
            style={{ ...input, width: '4.5rem' }}
            aria-label="Number of A4 sheets"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
          <button style={chip(scaleMode === 'fitted', '#7c3aed')} onClick={() => setScaleMode('fitted')}>
            Scale fitted to events
          </button>
          <button style={chip(scaleMode === 'even', '#7c3aed')} onClick={() => setScaleMode('even')}>
            Even scale
          </button>
          <button style={chip(!mono, '#b45309')} onClick={() => setMono(false)}>
            Colour
          </button>
          <button style={chip(mono, '#b45309')} onClick={() => setMono(true)}>
            Black and white
          </button>
          <button
            style={{ ...chip(true, '#be185d'), marginLeft: 'auto' }}
            onClick={() => window.print()}
          >
            Print
          </button>
        </div>
      </div>

      {daniel ? (
        <DanielSheet events={data.events} mono={mono} sprite={sprite} onSelect={select} />
      ) : (
        ranges.map((r, i) => (
        <Sheet
          key={`${r[0]}-${i}`}
          range={r}
          index={i}
          total={ranges.length}
          title={title}
          data={data}
          lanes={lanes}
          mono={mono}
          scaleMode={scaleMode}
          vignettes={vignettes}
          sprite={sprite}
          slug={slug}
          onSelect={select}
        />
        ))
      )}

      {selected && <Detail item={selected} onClose={() => setSelected(null)} card={card} />}
    </div>
  );
}

function Detail({ item, onClose, card }) {
  const g = item.gregorian_year ?? amToGregorian(item.am, EPOCH);
  const gEnd = item.gregorian_end ?? (item.amEnd != null ? amToGregorian(item.amEnd, EPOCH) : null);
  return (
    <div className="hc-controls" style={{ ...card, display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      {item.image && (
        <img
          src={item.image}
          alt={item.label}
          style={{ maxWidth: '12rem', maxHeight: '10rem', borderRadius: '0.4rem' }}
        />
      )}
      <div style={{ flex: '1 1 18rem' }}>
        <div style={{ fontWeight: 700, fontSize: '1rem' }}>{item.label}</div>
        <div style={{ fontSize: '0.85rem', color: theme.textMuted, margin: '0.2rem 0 0.5rem' }}>
          {formatYear(g)}
          {gEnd != null && gEnd !== g && Number.isFinite(gEnd) ? ` – ${formatYear(gEnd)}` : ''}
          {item.am != null && ` · AM ${Math.round(item.am)}`}
          {item.refs && ` · ${item.refs}`}
        </div>
        {(item.note || item.description || item.evidence) && (
          <p style={{ fontSize: '0.85rem', margin: '0 0 0.5rem' }}>
            {item.note ?? item.description ?? item.evidence}
          </p>
        )}
        {item.study_ref && (
          <a href={studyUrl(item.study_ref.split('#')[0])} style={{ fontSize: '0.85rem' }}>
            Read the study
          </a>
        )}
      </div>
      <button style={chip(false, '#64748b')} onClick={onClose} aria-label="Close">
        Close
      </button>
    </div>
  );
}

function Patterns({ mono }) {
  const s = mono ? 0.22 : 0.16;
  const line = (d) => <path d={d} stroke={INK} strokeWidth={s} fill="none" />;
  const pat = (id, size, children) => (
    <pattern id={`hc-${id}`} width={size} height={size} patternUnits="userSpaceOnUse">
      {children}
    </pattern>
  );
  return (
    <defs>
      {pat('dots', 2, <circle cx="1" cy="1" r={mono ? 0.32 : 0.25} fill={INK} />)}
      {pat('diag', 2.2, line('M0 2.2 L2.2 0'))}
      {pat('diag2', 2.2, line('M0 0 L2.2 2.2'))}
      {pat('horiz', 1.8, line('M0 0.9 H1.8'))}
      {pat('vert', 1.8, line('M0.9 0 V1.8'))}
      {pat('cross', 2.4, line('M0 2.4 L2.4 0 M0 0 L2.4 2.4'))}
      {pat('hatch', 1.2, <path d="M0 1.2 L1.2 0" stroke={INK} strokeWidth="0.2" />)}
      <linearGradient id="hc-fade">
        <stop offset="0" stopColor={PAPER} stopOpacity="0" />
        <stop offset="1" stopColor={PAPER} stopOpacity="1" />
      </linearGradient>
      <filter id="hc-mono">
        <feColorMatrix type="saturate" values="0" />
      </filter>
    </defs>
  );
}

function Sheet({ range, index, total, title, data, lanes, mono, scaleMode, vignettes, sprite, slug, onSelect }) {
  const svgRef = useRef(null);
  const { w: W, h: H, margin: M } = SHEET;
  const X0 = M + 21;
  const X1 = W - M;
  const [a, b] = range;
  const years = b - a;
  const inRange = (am, amEnd = am) => amEnd >= a && am <= b;

  // --- what is on this sheet ----------------------------------------------------------------
  const moved = new Set(data.movements.map((m) => m.event));
  const scriptureItems = [...data.movements, ...data.events.filter((e) => !moved.has(e.id))]
    .filter((e) => e.am != null && inRange(e.am))
    .filter(
      (e) =>
        e.source === 'movement' ||
        e.source === 'genesis' ||
        e.source === 'milestone' ||
        (e.source === 'anchor' && (e.core || years <= CORE_ONLY_SPAN)) ||
        (e.source === 'life' && years <= 700)
    )
    .map((e) => ({
      ...e,
      priority:
        e.source === 'movement' || e.source === 'milestone' || (e.source === 'genesis' && e.core)
          ? 0
          : e.source === 'anchor' && e.core
            ? 1
            : e.source === 'life'
              ? 3
              : 2,
    }))
    .sort((p, q) => p.priority - q.priority || p.am - q.am);
  const textItems = data.events
    .filter((e) => (e.source === 'artifact' || e.source === 'archaeology') && e.am != null)
    .filter((e) => inRange(e.am, e.am_end ?? e.am))
    .sort((p, q) => p.am - q.am);
  const level = peopleLevel(years);
  const people = data.people
    .filter((p) => (p.significance_level ?? 3) <= level && inRange(p.zadok_year_born, p.zadok_year_died))
    .sort(
      (p, q) =>
        (p.significance_level ?? 3) - (q.significance_level ?? 3) ||
        p.zadok_year_born - q.zadok_year_born
    );

  // Fitting needs something to fit: on a sparse sheet the folds would mark nothing, so it stays even.
  const marks = [...scriptureItems, ...textItems].map((e) => e.am);
  const scale = makeScale(a, b, X0, X1, marks.length >= 15 ? scaleMode : 'even', marks);
  const x = (am) => scale.x(Math.max(a, Math.min(b, am)));

  // --- vertical layout ----------------------------------------------------------------------
  const AXIS_AM = 25;
  const DAYS = [26.5, 35.5];
  const AGES = [36.5, 44];
  const PERIODS_BAND = [44.8, 50.6];
  const BODY = [52, 182.5];
  const AXIS_G = 185;
  const laneWeights = { scripture: lanes.pictures ? 3.4 : 2.2, people: 1.4, texts: 1.5 };
  const shown = ['scripture', 'people', 'texts'].filter((id) => lanes[id]);
  const totalWeight = shown.reduce((s, id) => s + laneWeights[id], 0);
  const laneBox = {};
  let y = BODY[0];
  for (const id of shown) {
    const hgt = ((BODY[1] - BODY[0]) * laneWeights[id]) / totalWeight;
    laneBox[id] = [y, y + hgt];
    y += hgt;
  }

  const els = [];

  // --- ages: a wash behind the body and a ribbon naming each ----------------------------------
  const ageStyle = (id) => AGE_STYLE[id] ?? { tint: '#ffffff', pattern: null };
  for (const age of data.ages) {
    if (!inRange(age.am, Math.min(age.amEnd, 1e6))) continue;
    const ax0 = x(age.am);
    const ax1 = x(Math.min(age.amEnd, b));
    const st = ageStyle(age.id);
    const fill = mono ? '#ffffff' : st.tint;
    const fadeFrom = age.open_end && Number.isFinite(age.amEnd) ? Math.max(data.now, age.am) : null;
    els.push(
      <g key={`age-${age.id}`} onClick={() => onSelect({ ...age, label: `${age.label} (${age.term})` })} style={{ cursor: 'pointer' }}>
        <rect x={ax0} y={AGES[0]} width={ax1 - ax0} height={BODY[1] - AGES[0]} fill={fill} opacity={mono ? 1 : 0.55} />
        {st.pattern && (
          <rect x={ax0} y={AGES[0]} width={ax1 - ax0} height={AGES[1] - AGES[0]} fill={`url(#hc-${st.pattern})`} opacity={mono ? 0.7 : 0.45} />
        )}
        {st.pattern && mono && (
          <rect x={ax0} y={BODY[0]} width={ax1 - ax0} height={BODY[1] - BODY[0]} fill={`url(#hc-${st.pattern})`} opacity="0.18" />
        )}
        {fadeFrom != null && fadeFrom < b && (
          <rect x={x(fadeFrom)} y={AGES[0]} width={ax1 - x(fadeFrom)} height={BODY[1] - AGES[0]} fill="url(#hc-fade)" />
        )}
        <rect x={ax0} y={AGES[0]} width={ax1 - ax0} height={AGES[1] - AGES[0]} fill="none" stroke={INK} strokeWidth="0.25" />
        <title>{`${age.label} (${age.term}), ${age.refs}`}</title>
        {(() => {
          const fit = fitLabel([`${age.label} · ${age.term}`, age.label, age.term], ax1 - ax0 - 1.5);
          return (
            fit && (
              <text x={(ax0 + ax1) / 2} y={AGES[1] - 2.4} fontSize={fit.size} textAnchor="middle" fontWeight="bold" fill={INK} style={{ paintOrder: 'stroke' }} stroke={mono ? '#ffffff' : st.tint} strokeWidth="0.8">
                {fit.t}
              </text>
            )
          );
        })()}
      </g>
    );
    if (fadeFrom != null && fadeFrom < b && x(age.amEnd) - x(fadeFrom) > 30) {
      els.push(
        <text key={`age-open-${age.id}`} x={(x(fadeFrom) + ax1) / 2} y={BODY[0] + 3.5} fontSize="2" textAnchor="middle" fontStyle="italic" fill={MUTED}>
          its end not dated (Mark 13:32)
        </text>
      );
    }
  }

  // --- periods: the stretches inside the ages, with each exile and return marked ---------------
  for (const pd of data.periods) {
    if (!inRange(pd.am, pd.amEnd)) continue;
    const px0 = x(pd.am);
    const px1 = x(Math.min(pd.amEnd, b));
    const fit = fitLabel([pd.label], px1 - px0 - 1, [2.2, 1.9, 1.6]);
    els.push(
      <g key={`period-${pd.id}`} onClick={() => onSelect(pd)} style={{ cursor: 'pointer' }}>
        <rect x={px0} y={PERIODS_BAND[0]} width={px1 - px0} height={PERIODS_BAND[1] - PERIODS_BAND[0]} fill={pd.id === 'exile' && !mono ? '#efe1d0' : '#ffffff'} stroke={INK} strokeWidth="0.25" />
        {pd.id === 'exile' && <rect x={px0} y={PERIODS_BAND[0]} width={px1 - px0} height={PERIODS_BAND[1] - PERIODS_BAND[0]} fill="url(#hc-hatch)" opacity="0.35" />}
        {fit && (
          <text x={(px0 + px1) / 2} y={PERIODS_BAND[1] - 1.9} fontSize={fit.size} textAnchor="middle" fill={INK} stroke="#ffffff" strokeWidth="0.6" style={{ paintOrder: 'stroke' }}>
            {fit.t}
          </text>
        )}
        <title>{`${pd.label} (${pd.refs})`}</title>
      </g>
    );
  }
  for (const m of data.movements) {
    if (!inRange(m.am)) continue;
    els.push(
      <g key={`band-${m.id}`}>
        <Arrow x={x(m.am)} y={PERIODS_BAND[0] + 1.6} out={m.direction === 'out'} mono={mono} />
        <title>{`${m.label}, ${formatYear(m.gregorian_year)} (${m.refs})`}</title>
      </g>
    );
  }

  // --- creation days: each day of the week over its thousand years ----------------------------
  const days = [
    ...CHRONOLOGY.millennial_days.map((d) => ({ n: d.day, am0: d.am_start, am1: d.am_end })),
    { n: 8, am0: CHRONOLOGY.eighth_day.am_start, am1: Infinity },
  ];
  const DAY_NOTES = { 7: 'rest · the thousand years', 8: 'the new creation' };
  for (const d of days) {
    if (!inRange(d.am0, Math.min(d.am1, 1e6))) continue;
    const dx0 = x(d.am0);
    const dx1 = x(Math.min(d.am1, b));
    const wd = dx1 - dx0;
    els.push(
      <g key={`day-${d.n}`}>
        <rect x={dx0} y={DAYS[0]} width={wd} height={DAYS[1] - DAYS[0]} fill={mono ? '#ffffff' : '#f3ead6'} stroke={INK} strokeWidth="0.25" />
        {sprite && wd > 9 && <use href={`#day-${d.n}`} x={dx0 + 1} y={DAYS[0] + 0.8} width="7.4" height="7.4" />}
        {wd > 14 && (
          <text x={dx0 + (wd > 9 ? 9.4 : 1)} y={DAYS[0] + 4} fontSize="2.6" fontWeight="bold" fill={INK}>
            {`Day ${d.n}`}
          </text>
        )}
        {wd > 30 && (
          <text x={dx0 + 9.4} y={DAYS[0] + 7.2} fontSize="1.9" fill={MUTED}>
            {DAY_NOTES[d.n] ?? `AM ${d.am0}–${d.am1}`}
          </text>
        )}
      </g>
    );
    if (d.am0 > a && d.am0 < b) {
      els.push(
        <line key={`dayline-${d.n}`} x1={dx0} x2={dx0} y1={DAYS[1]} y2={BODY[1]} stroke={INK} strokeWidth="0.25" strokeDasharray="1 1" opacity="0.6" />
      );
    }
  }

  // --- lane labels ----------------------------------------------------------------------------
  const LANE_NAMES = { scripture: ['Scripture', 'and history'], people: ['People'], texts: ['Texts', 'and finds'] };
  for (const id of shown) {
    const [y0, y1] = laneBox[id];
    els.push(
      <g key={`lane-${id}`}>
        <line x1={M} x2={X1} y1={y1} y2={y1} stroke={INK} strokeWidth="0.2" opacity="0.5" />
        {LANE_NAMES[id].map((t, k) => (
          <text key={t} x={M} y={(y0 + y1) / 2 + k * 3} fontSize="2.4" fontWeight={k ? 'normal' : 'bold'} fill={INK}>
            {t}
          </text>
        ))}
      </g>
    );
  }
  els.push(
    <g key="axis-labels">
      <text x={M} y={AXIS_AM - 1.2} fontSize="2.2" fontWeight="bold" fill={INK}>Anno Mundi</text>
      <text x={M} y={(DAYS[0] + DAYS[1]) / 2 + 1} fontSize="2.2" fontWeight="bold" fill={INK}>The week</text>
      <text x={M} y={(AGES[0] + AGES[1]) / 2 + 1} fontSize="2.2" fontWeight="bold" fill={INK}>The ages</text>
      <text x={M} y={(PERIODS_BAND[0] + PERIODS_BAND[1]) / 2 + 1} fontSize="2.2" fontWeight="bold" fill={INK}>The periods</text>
      <text x={M} y={AXIS_G + 3.4} fontSize="2.2" fontWeight="bold" fill={INK}>BC / AD</text>
    </g>
  );

  // --- scripture lane: pictures above, labels stacked on a baseline ----------------------------
  const pictureIds = new Set();
  if (lanes.scripture) {
    const [y0, y1] = laneBox.scripture;
    const threadTrack = lanes.threads ? 7 : 0;
    const base = y1 - threadTrack - 1.5;
    let rowsTop = y0 + 2;
    if (lanes.pictures && sprite && y1 - y0 > 48) {
      const CW = 26;
      const CH = 19.5;
      const callouts = placeCallouts(
        scriptureItems.filter((e) => vignettes.has(e.id)).map((e) => ({ ...e, x: x(e.am) })),
        CW,
        X0,
        X1
      );
      for (const c of callouts) {
        pictureIds.add(c.id);
        const cy = y0 + 2;
        els.push(
          <g key={`pic-${c.id}`} onClick={() => onSelect(c)} style={{ cursor: 'pointer' }}>
            <line x1={c.cx + CW / 2} x2={c.x} y1={cy + CH + 7.8} y2={base} stroke={INK} strokeWidth="0.2" strokeDasharray="0.8 0.6" />
            <circle cx={c.x} cy={base} r="0.7" fill={INK} />
            <rect x={c.cx - 0.6} y={cy - 0.6} width={CW + 1.2} height={CH + 1.2} fill={PAPER} stroke={INK} strokeWidth="0.35" />
            <svg x={c.cx} y={cy} width={CW} height={CH} viewBox="0 0 240 180" style={mono ? { filter: 'url(#hc-mono)' } : undefined}>
              <use href={`#v-${c.id}`} />
            </svg>
            {wrap2(c.label, CW + 1, 2.1).map((line, k) => (
              <text key={k} x={c.cx + CW / 2} y={cy + CH + 2.6 + k * 2.4} fontSize="2.1" textAnchor="middle" fontWeight="bold" fill={INK}>
                {line}
              </text>
            ))}
            <text x={c.cx + CW / 2} y={cy + CH + 7.2} fontSize="1.9" textAnchor="middle" fill={MUTED}>
              {dateOf(c.am, data.now)}
            </text>
            <title>{`${c.label}${c.refs ? ` (${c.refs})` : ''}`}</title>
          </g>
        );
      }
      rowsTop = y0 + CH + 11;
    }
    const ROW = 3.1;
    const maxRows = Math.max(0, Math.floor((base - rowsTop) / ROW));
    const labelled = scriptureItems
      .filter((e) => !pictureIds.has(e.id))
      .map((e) => {
        const ex = x(e.am);
        const label = `${e.label}  ${dateOf(e.am, data.now)}`;
        const wd = textWidth(label, 2.1) + 1.2;
        const right = ex + wd > X1;
        return { ...e, ex, text: label, right, x0: right ? ex - wd : ex - 0.6, x1: right ? ex + 0.6 : ex + wd };
      });
    const { placed, dropped } = packRows(labelled, maxRows);
    for (const p of placed) {
      const ly = base - 2.2 - p.row * ROW;
      els.push(
        <g key={`ev-${p.id}`} onClick={() => onSelect(p)} style={{ cursor: 'pointer' }}>
          <line x1={p.ex} x2={p.ex} y1={base} y2={ly + 0.6} stroke={INK} strokeWidth="0.15" opacity="0.6" />
          {p.source === 'movement' ? (
            <Arrow x={p.ex} y={base} out={p.direction === 'out'} mono={mono} />
          ) : (
            <circle cx={p.ex} cy={base} r="0.6" fill={p.source === 'milestone' ? RED : INK} />
          )}
          <text x={p.right ? p.ex - 0.8 : p.ex + 0.8} y={ly} fontSize="2.1" textAnchor={p.right ? 'end' : 'start'} fill={INK} stroke={PAPER} strokeWidth="0.6" style={{ paintOrder: 'stroke' }}>
            {p.label}
            <tspan fill={MUTED} fontSize="1.8">{`  ${dateOf(p.am, data.now)}`}</tspan>
          </text>
          <title>{`${p.label}${p.refs ? ` (${p.refs})` : ''}`}</title>
        </g>
      );
    }
    els.push(<line key="scripture-base" x1={X0} x2={X1} y1={base} y2={base} stroke={INK} strokeWidth="0.3" />);
    if (dropped) els.push(more('scripture', X1, y0 + 2.6, dropped));

    // --- threads: a ribbon through events, an arc over a counted prophecy ----------------------
    if (lanes.threads) {
      data.threads.forEach((t, k) => {
        const st = THREAD_STYLE[t.id] ?? { color: INK, dash: null };
        const color = mono ? INK : st.color;
        const ty = base + 2.2 + k * 1.7;
        const visible = t.points.filter((p) => inRange(p.am));
        if (t.kind === 'arc') {
          const [p0, p1] = [t.points[0], t.points[t.points.length - 1]];
          if (!inRange(p0.am, p1.am)) return;
          const ax0 = x(p0.am);
          const ax1 = x(p1.am);
          const top = base - 14;
          els.push(
            <g key={`thread-${t.id}`} onClick={() => onSelect({ ...t, am: p0.am, amEnd: p1.am })} style={{ cursor: 'pointer' }}>
              <path d={`M${ax0} ${base} Q${(ax0 + ax1) / 2} ${top} ${ax1} ${base}`} fill="none" stroke={color} strokeWidth="0.55" strokeDasharray={st.dash ?? undefined} />
              <text x={(ax0 + ax1) / 2} y={(base + top) / 2 - 0.6} fontSize="2" textAnchor="middle" fontStyle="italic" fill={color} stroke={PAPER} strokeWidth="0.6" style={{ paintOrder: 'stroke' }}>
                {t.span_label ? `${t.label}: ${t.span_label}` : t.label}
              </text>
              <title>{`${t.label} (${t.refs})`}</title>
            </g>
          );
          return;
        }
        if (!t.points.some((p, i) => i && inRange(t.points[i - 1].am, p.am))) return;
        const xs = t.points.map((p) => scale.x(p.am));
        const clipX = (v) => Math.max(X0, Math.min(X1, v));
        const seg = [];
        for (let i = 0; i < xs.length - 1; i++) {
          if (!inRange(t.points[i].am, t.points[i + 1].am)) continue;
          seg.push(`M${clipX(xs[i])} ${ty} H${clipX(xs[i + 1])}`);
        }
        els.push(
          <g key={`thread-${t.id}`} onClick={() => onSelect({ ...t, am: t.points[0].am })} style={{ cursor: 'pointer' }}>
            <path d={seg.join(' ')} stroke={color} strokeWidth="0.6" strokeDasharray={st.dash ?? undefined} fill="none" />
            {visible.map((p) => (
              <circle key={p.id} cx={x(p.am)} cy={ty} r="0.75" fill={PAPER} stroke={color} strokeWidth="0.4" />
            ))}
            <text x={Math.min(clipX(xs[0]) + 1, X1 - textWidth(t.label, 1.7))} y={ty - 0.5} fontSize="1.7" fill={color} stroke={PAPER} strokeWidth="0.5" style={{ paintOrder: 'stroke' }}>
              {t.label}
            </text>
            <title>{`${t.label}: ${t.points.map((p) => p.label).join(' → ')} (${t.refs})`}</title>
          </g>
        );
      });
    }
  }

  // --- people lane: lifespans ---------------------------------------------------------------
  if (lanes.people) {
    const [y0, y1] = laneBox.people;
    const ROW = 3.3;
    const maxRows = Math.max(0, Math.floor((y1 - y0 - 2) / ROW));
    const bars = people.map((p) => {
      const bx0 = x(p.zadok_year_born);
      const bx1 = x(p.zadok_year_died);
      const nameW = textWidth(p.name, 2) + 1;
      const inside = bx1 - bx0 > nameW + 1;
      return { ...p, bx0, bx1, inside, x0: bx0, x1: inside ? bx1 : Math.min(X1 + 40, bx1 + nameW + 0.6) };
    });
    const { placed, dropped } = packRows(bars, maxRows, 0.8);
    for (const p of placed) {
      const by = y0 + 1.5 + p.row * ROW;
      const estimated = p.data_classification && p.data_classification !== 'ACTUAL';
      els.push(
        <g
          key={`p-${p.id}`}
          onClick={() =>
            onSelect({ ...p, label: p.name, am: p.zadok_year_born, amEnd: p.zadok_year_died, refs: (p.bible_references ?? []).slice(0, 3).join('; '), note: p.title })
          }
          style={{ cursor: 'pointer' }}
        >
          <rect x={p.bx0} y={by} width={Math.max(0.6, p.bx1 - p.bx0)} height="2.4" fill={mono ? '#ffffff' : '#c9d6e6'} stroke={INK} strokeWidth="0.2" />
          {estimated && <rect x={p.bx0} y={by} width={Math.max(0.6, p.bx1 - p.bx0)} height="2.4" fill="url(#hc-hatch)" opacity="0.6" />}
          <text x={p.inside ? p.bx0 + 0.8 : p.bx1 + 0.6} y={by + 1.85} fontSize="2" fill={INK} fontWeight={p.significance_level === 1 ? 'bold' : 'normal'}>
            {p.name}
          </text>
          <title>{`${p.name}: ${formatYear(amToGregorian(p.zadok_year_born, EPOCH))} – ${formatYear(amToGregorian(p.zadok_year_died, EPOCH))}, ${p.lifespan_years ?? ''} years`}</title>
        </g>
      );
    }
    if (dropped) els.push(more('people', X1, y0 + 2.6, dropped));
    if (!placed.length)
      els.push(
        <text key="people-none" x={X0 + 2} y={(y0 + y1) / 2} fontSize="2" fontStyle="italic" fill={MUTED}>
          The genealogy ends with Jesus; no one in it lived in these years.
        </text>
      );
  }

  // --- texts and finds lane: manuscripts, inscriptions, historians, dated records -------------
  if (lanes.texts) {
    const [y0, y1] = laneBox.texts;
    const ROW = 4.4;
    const base = y1 - 1.2;
    const maxRows = Math.max(0, Math.floor((base - y0 - 1) / ROW));
    const items = textItems.map((e) => {
      const ex = x(e.am);
      const ex1 = x(e.am_end ?? e.am);
      const kind = e.kind ?? 'archaeology';
      const wd = 4.6 + textWidth(e.label, 2) + 1;
      const right = ex + wd > X1;
      return { ...e, kind, ex, ex1, right, x0: right ? ex - wd : ex - 2.2, x1: right ? ex + 2.2 : ex + wd };
    });
    const { placed, dropped } = packRows(items, maxRows, 0.8);
    for (const p of placed) {
      const iy = base - 4.6 - p.row * ROW;
      els.push(
        <g key={`t-${p.id}`} onClick={() => onSelect(p)} style={{ cursor: 'pointer' }}>
          {p.ex1 - p.ex > 0.8 && <rect x={p.ex} y={base - 0.5} width={p.ex1 - p.ex} height="1" fill={INK} opacity="0.55" />}
          <line x1={p.ex} x2={p.ex} y1={base} y2={iy + 4} stroke={INK} strokeWidth="0.15" opacity="0.6" />
          {sprite && <use href={`#kind-${p.kind}`} x={p.ex - 2} y={iy} width="4" height="4" />}
          <text x={p.right ? p.ex - 2.4 : p.ex + 2.4} y={iy + 2.9} fontSize="2" textAnchor={p.right ? 'end' : 'start'} fill={INK} stroke={PAPER} strokeWidth="0.6" style={{ paintOrder: 'stroke' }}>
            {p.label}
          </text>
          <title>{`${KIND_LABEL[p.kind]}: ${p.label}${p.refs ? ` (${p.refs})` : ''}`}</title>
        </g>
      );
    }
    els.push(<line key="texts-base" x1={X0} x2={X1} y1={base} y2={base} stroke={INK} strokeWidth="0.3" />);
    if (dropped) els.push(more('texts', X1, y0 + 2.6, dropped));
    if (!placed.length)
      els.push(
        <text key="texts-none" x={X0 + 2} y={(y0 + y1) / 2} fontSize="2" fontStyle="italic" fill={MUTED}>
          No catalogued text or find is dated in these years.
        </text>
      );
  }

  // --- today ---------------------------------------------------------------------------------
  if (inRange(data.now)) {
    const nx = x(data.now);
    els.push(
      <g key="now">
        <line x1={nx} x2={nx} y1={DAYS[1]} y2={BODY[1]} stroke={RED} strokeWidth="0.4" strokeDasharray="1.2 0.8" />
        <text x={nx - 0.8} y={BODY[1] - 1.4} fontSize="2.1" textAnchor="end" fontWeight="bold" fill={RED} stroke={PAPER} strokeWidth="0.6" style={{ paintOrder: 'stroke' }}>
          {`Today, ${formatYear(amToGregorian(data.now, EPOCH))}`}
        </text>
      </g>
    );
  }

  // --- axes: Anno Mundi above, BC/AD below, a fold wherever the scale changes ------------------
  const axis = [];
  axis.push(<line key="am-line" x1={X0} x2={X1} y1={AXIS_AM} y2={AXIS_AM} stroke={INK} strokeWidth="0.35" />);
  axis.push(<line key="g-line" x1={X0} x2={X1} y1={AXIS_G} y2={AXIS_G} stroke={INK} strokeWidth="0.35" />);
  const spaced = (ticks, xOf, gap) => {
    const out = [];
    for (const t of ticks) if (!out.length || xOf(t) - xOf(out[out.length - 1]) >= gap) out.push(t);
    return out;
  };
  for (const am of spaced(amTicks(scale.segments).filter((v) => v <= 7000), x, 8)) {
    const tx = x(am);
    axis.push(
      <g key={`amt-${am}`}>
        <line x1={tx} x2={tx} y1={AXIS_AM - 0.9} y2={AXIS_AM} stroke={INK} strokeWidth="0.25" />
        <text x={tx} y={AXIS_AM - 1.4} fontSize="2" textAnchor="middle" fill={INK}>{am}</text>
      </g>
    );
  }
  const gTicks = gregorianTicks(scale.segments).filter((t) => t.am <= data.now);
  const futureNote = b > data.now && X1 - x(Math.max(a, data.now)) > 26;
  if (futureNote)
    axis.push(
      <text key="g-future" x={X1} y={AXIS_G + 3.2} fontSize="2" textAnchor="end" fontStyle="italic" fill={MUTED}>
        not dated (Mark 13:32)
      </text>
    );
  const lastTickX = futureNote ? X1 - textWidth('not dated (Mark 13:32)', 2) - 6 : Infinity;
  for (const { g, am } of spaced(gTicks, (t) => x(t.am), 9).filter((t) => x(t.am) < lastTickX)) {
    const tx = x(am);
    axis.push(
      <g key={`gt-${g}`}>
        <line x1={tx} x2={tx} y1={AXIS_G} y2={AXIS_G + 0.9} stroke={INK} strokeWidth="0.25" />
        <text x={tx} y={AXIS_G + 3.2} fontSize="2" textAnchor="middle" fill={INK}>{formatYear(g)}</text>
      </g>
    );
  }
  if (scale.segments.length > 1) {
    scale.segments.forEach((sg, k) => {
      if (k > 0)
        for (const ay of [AXIS_AM, AXIS_G])
          axis.push(
            <path key={`fold-${k}-${ay}`} d={`M${sg.x0 - 0.7} ${ay - 1.2} l0.7 0.8 l0.7 -0.8 l-0.7 2.4`} fill="none" stroke={INK} strokeWidth="0.3" />
          );
      if (sg.x1 - sg.x0 > 13)
        axis.push(
          <text key={`ypc-${k}`} x={(sg.x0 + sg.x1) / 2} y={AXIS_G + 6} fontSize="1.7" textAnchor="middle" fill={MUTED} fontStyle="italic">
            {`${niceYears(sg.yearsPerCm)} yrs/cm`}
          </text>
        );
    });
  }

  // --- title, locator, footer ----------------------------------------------------------------
  const ga = formatYear(amToGregorian(Math.round(a), EPOCH));
  // Past today the chart gives the week's AM count and no calendar year.
  const gb = b > data.now ? 'the years not yet dated' : formatYear(amToGregorian(Math.round(b), EPOCH));
  const even = scale.segments.length === 1;
  const ypc = scale.segments[0].yearsPerCm;
  const weekMetres = even ? ((7000 / ypc) * 10) / 1000 : null;
  const scaleNote = even
    ? `1 cm = ${niceYears(ypc)} years${weekMetres > 0.4 ? `; the whole week at this scale would be ${weekMetres < 10 ? weekMetres.toFixed(1) : Math.round(weekMetres)} m long` : ''}`
    : 'Scale fitted to the events: a fold on the axis marks each change, with its years per centimetre';
  const LW = 78;
  const LX = X1 - LW;
  const lx = (am) => LX + (Math.max(0, Math.min(7400, am)) / 7400) * LW;

  const download = () =>
    downloadSvg(svgRef.current, sprite, `history-chart-${slug}${total > 1 ? `-${index + 1}` : ''}.svg`);

  return (
    <div className="hc-sheet-wrap" style={{ marginBottom: '1rem' }}>
      <svg
        ref={svgRef}
        className="hc-sheet"
        viewBox={`0 0 ${W} ${H}`}
        style={{ width: '100%', height: 'auto', display: 'block', background: PAPER, boxShadow: '0 1px 6px #0003', fontFamily: SERIF }}
        role="img"
        aria-label={`History chart, ${title}, sheet ${index + 1} of ${total}`}
      >
        <Patterns mono={mono} />
        <rect x="0" y="0" width={W} height={H} fill={PAPER} />
        <rect x={M - 3} y={M - 3} width={W - 2 * M + 6} height={H - 2 * M + 6} fill="none" stroke={INK} strokeWidth="0.5" />
        <text x={M} y={M + 5} fontSize="5.4" fontWeight="bold" fill={INK}>The Millennial Week</text>
        <text x={M} y={M + 10} fontSize="2.7" fill={INK}>
          {`${title}${total > 1 ? ` · sheet ${index + 1} of ${total}` : ''} · AM ${Math.round(a)}–${Math.round(Math.min(b, 1e6))} · ${ga} to ${gb}`}
        </text>
        <text x={M} y={M + 13.6} fontSize="2" fill={MUTED} fontStyle="italic">{scaleNote}</text>

        <g>
          <text x={LX} y={M + 1.2} fontSize="1.9" fill={MUTED}>Where this sheet sits in the week</text>
          <rect x={LX} y={M + 2.2} width={LW} height="4.4" fill="#ffffff" stroke={INK} strokeWidth="0.25" />
          {days.slice(0, 7).map((d) => (
            <g key={`loc-${d.n}`}>
              <line x1={lx(d.am0)} x2={lx(d.am0)} y1={M + 2.2} y2={M + 6.6} stroke={INK} strokeWidth="0.15" />
              <text x={lx(d.am0 + 500)} y={M + 9} fontSize="1.6" textAnchor="middle" fill={MUTED}>{d.n}</text>
            </g>
          ))}
          <rect x={lx(a)} y={M + 2.2} width={Math.max(0.8, lx(b) - lx(a))} height="4.4" fill={mono ? INK : RED} opacity="0.55" />
        </g>

        {els}
        {axis}

        <g fontSize="1.9" fill={INK}>
          {sprite &&
            Object.entries(KIND_LABEL).map(([k, label], i) => (
              <g key={k}>
                <use href={`#kind-${k}`} x={M + i * 30} y={H - M - 4.2} width="3.4" height="3.4" />
                <text x={M + i * 30 + 4} y={H - M - 1.6}>{label}</text>
              </g>
            ))}
          <rect x={M + 116} y={H - M - 3.6} width="6" height="2.2" fill="url(#hc-hatch)" stroke={INK} strokeWidth="0.2" />
          <text x={M + 123} y={H - M - 1.6}>Calculated or estimated</text>
          <Arrow x={M + 152} y={H - M - 3.4} out mono={mono} />
          <text x={M + 154} y={H - M - 1.6}>Exile</text>
          <Arrow x={M + 164} y={H - M - 3.4} out={false} mono={mono} />
          <text x={M + 166} y={H - M - 1.6}>Return</text>
          {lanes.threads &&
            data.threads.map((t, i) => {
              const st = THREAD_STYLE[t.id] ?? { color: INK, dash: null };
              return (
                <g key={`leg-${t.id}`}>
                  <line x1={M + 180 + i * 27} x2={M + 185 + i * 27} y1={H - M - 2.3} y2={H - M - 2.3} stroke={mono ? INK : st.color} strokeWidth="0.6" strokeDasharray={st.dash ?? undefined} />
                  <text x={M + 186 + i * 27} y={H - M - 1.6}>{t.label}</text>
                </g>
              );
            })}
          <text x={X1} y={H - M + 1.6} fontSize="1.7" textAnchor="end" fill={MUTED}>
            {`${PAGE_URL}${window.location.hash}`}
          </text>
        </g>
      </svg>
      <div className="hc-controls" style={{ textAlign: 'right', marginTop: '0.3rem' }}>
        <button style={chip(false, '#64748b')} onClick={download}>
          {`Download sheet ${index + 1} as SVG`}
        </button>
      </div>
    </div>
  );
}

// A future event has a place in the week and no date: "concerning that day and hour no one knows"
// (Mark 13:32). The arithmetic of the week reaches AM 6000; the chart prints that, never a BC/AD year.
function dateOf(am, now) {
  return am > now ? `AM ${Math.round(am)}` : formatYear(amToGregorian(am, EPOCH));
}

// Labels shrink a step before they are dropped: a narrow age keeps its name.
function fitLabel(options, room, sizes = [2.5, 2.1, 1.8]) {
  for (const t of options) for (const size of sizes) if (textWidth(t, size) <= room) return { t, size };
  return null;
}

// Two lines under a picture, the second cut short if it must be.
function wrap2(s, widthMm, size) {
  const max = Math.floor(widthMm / (size * 0.5));
  if (s.length <= max) return [s];
  const cut = s.lastIndexOf(' ', max);
  const first = cut > 0 ? s.slice(0, cut) : s.slice(0, max);
  return [first, trim(s.slice(first.length).trim(), widthMm, size)];
}

// ▼ away from the land, ▲ back to it. Filled and hollow as well as coloured, so they print in mono.
function Arrow({ x, y, out, mono }) {
  const d = out ? `M${x - 1.2} ${y - 1} H${x + 1.2} L${x} ${y + 1.1} Z` : `M${x - 1.2} ${y + 1} H${x + 1.2} L${x} ${y - 1.1} Z`;
  const color = mono ? INK : out ? RED : '#2f6f3f';
  return <path d={d} fill={out ? color : PAPER} stroke={color} strokeWidth="0.35" />;
}

// A sheet as a standalone SVG file, with the pictures it uses carried inside it.
function downloadSvg(node, sprite, name) {
  if (!node) return;
  const clone = node.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('width', '297mm');
  clone.setAttribute('height', '210mm');
  const defs = sprite.replace(/^<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
  const body = clone.outerHTML.replace(/^<svg([^>]*)>/, `<svg$1><defs>${defs}</defs>`);
  const url = URL.createObjectURL(new window.Blob([body], { type: 'image/svg+xml' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

function DanielSheet({ events, mono, sprite, onSelect }) {
  const svgRef = useRef(null);
  return (
    <div className="hc-sheet-wrap" style={{ marginBottom: '1rem' }}>
      <DanielKingdoms events={events} mono={mono} onSelect={onSelect} svgRef={svgRef} />
      <div className="hc-controls" style={{ textAlign: 'right', marginTop: '0.3rem' }}>
        <button style={chip(false, '#64748b')} onClick={() => downloadSvg(svgRef.current, sprite, 'daniels-kingdoms.svg')}>
          Download as SVG
        </button>
      </div>
    </div>
  );
}

function more(id, xr, yy, n) {
  return (
    <text key={`more-${id}`} x={xr} y={yy} fontSize="1.8" textAnchor="end" fontStyle="italic" fill={MUTED}>
      {`+${n} more: add sheets or narrow the years`}
    </text>
  );
}

function trim(s, widthMm, size) {
  const max = Math.floor(widthMm / (size * 0.5));
  return s.length <= max ? s : `${s.slice(0, max - 1)}…`;
}

function niceYears(v) {
  if (v >= 100) return String(Math.round(v / 10) * 10);
  if (v >= 10) return String(Math.round(v));
  return v.toFixed(1);
}
