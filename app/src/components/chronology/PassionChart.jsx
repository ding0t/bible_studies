import React, { useEffect, useMemo, useRef, useState } from 'react';
import { CHRONOLOGY } from '../../utils/chronology';
import { SHEET, packRows, placeCallouts, textWidth } from '../../utils/historyChart';
import { chip, studyUrl, theme } from './shared';
import { civilDay, clock, gospelHour } from './DatedSequence';

// The printable chart for the AD 33 periods (Passion week, the betrayal, the crucifixion, the three
// days, the resurrection, Passover to Pentecost): one A4 sheet whose axis is the period's hours,
// drawn from the same passion_sequence the Timeline reads. Like the Timeline, a period of two days
// or less shows the hour-by-hour detail events and a wider one shows the summaries.
const SERIF = "Georgia, 'Times New Roman', serif";
const INK = '#3b2f1e';
const MUTED = '#6b5a3e';
const PAPER = '#faf6ec';
const RED = '#8b1e1e';
const SPRITES_URL = '/assets/chart/sprites.svg';
const CW = 30;
const CH = 22.5;
const ROW = 3.9;
const SIZE = 2.5;

const TRACKS = [
  { id: 'jesus', label: 'Jesus', color: '#2563eb', maxRows: 40 },
  { id: 'feasts', label: 'Appointed times (Leviticus 23)', color: '#b45309', maxRows: 6 },
  { id: 'church', label: 'The disciples', color: '#7c3aed', maxRows: 3 },
];
const CERTAINTY_RANK = { stated: 0, 'site-reading': 1, contested: 2 };

// Two lines under a picture, the second cut short if it must be.
function wrap2(label, widthMm, size) {
  const max = Math.floor(widthMm / (size * 0.5));
  if (label.length <= max) return [label];
  const cut = label.lastIndexOf(' ', max);
  const first = cut > 0 ? label.slice(0, cut) : label.slice(0, max);
  const rest = label.slice(first.length).trim();
  return [first, rest.length <= max ? rest : `${rest.slice(0, max - 1)}…`];
}

export function Sheet({ period, mono, pictures, vignettes, svgRef, onSelect }) {
  const P = CHRONOLOGY.passion_sequence;
  const { w: W, h: H, margin: M } = SHEET;
  const [start, end] = period.dated;
  const span = end - start;
  const hourly = span <= 48;
  const L = M + 20;
  const R = W - M - 2;
  const x = (h) => L + ((Math.min(Math.max(h, start), end) - start) / span) * (R - L);
  const inRange = (a, b = a) => b >= start && a <= end;
  const ink = (c) => (mono ? INK : c);
  const hebrewOf = (h) => P.days.find((d) => d.start <= h && h < d.end)?.hebrew;
  const when = (h, h2) => {
    const first = `${civilDay(Math.floor(h / 24))}, about ${clock(h)}`;
    const heb = hebrewOf(h);
    if (h2 == null) return `${first}${heb ? ` · ${heb}` : ''}`;
    const sameDay = Math.floor(h / 24) === Math.floor(h2 / 24);
    const second = sameDay ? clock(h2) : `${civilDay(Math.floor(h2 / 24))}, ${clock(h2)}`;
    return `${first} – ${second}${heb ? ` · from ${heb}` : ''}`;
  };

  const els = [];
  const dayTop = 26;
  const dayH = 10;

  // Hebrew days: night shaded, Sabbaths tinted
  for (const d of P.days.filter((d) => inRange(d.start, d.end))) {
    const a = x(d.start);
    const b = x(d.end);
    els.push(
      <g key={`day-${d.k}`}>
        <rect x={a} y={dayTop} width={x(d.start + 12) - a} height={H - M - dayTop - 14} fill="#1e293b" opacity={mono ? 0.07 : 0.08} />
        {d.sabbath && <rect x={a} y={dayTop} width={b - a} height={H - M - dayTop - 14} fill={ink('#b45309')} opacity="0.08" />}
        <line x1={a} x2={a} y1={dayTop} y2={H - M - 14} stroke={INK} strokeWidth="0.15" opacity="0.5" />
        {b - a > textWidth(d.hebrew, 2.1) + 1.6 && (
          <>
            <text x={a + 0.8} y={dayTop + 3.4} fontSize="2.1" fontWeight="bold" fill={INK}>
              {d.sabbath && b - a > textWidth(`${d.hebrew} · Sabbath`, 2.1) + 1.6 ? `${d.hebrew} · Sabbath` : d.hebrew}
            </text>
            {b - a > 22 && (
              <text x={a + 0.8} y={dayTop + 6.4} fontSize="1.7" fill={MUTED}>
                daylight: {d.daylight}
              </text>
            )}
          </>
        )}
      </g>
    );
  }
  els.push(<line key="day-base" x1={L} x2={R} y1={dayTop + dayH} y2={dayTop + dayH} stroke={INK} strokeWidth="0.35" />);

  // Hour ruler
  let top = dayTop + dayH;
  if (hourly) {
    const step = (R - L) / span >= 7 ? 1 : 2;
    for (let h = Math.ceil(start / step) * step; h <= end; h += step) {
      const px = x(h);
      els.push(
        <g key={`h-${h}`}>
          <line x1={px} x2={px} y1={top} y2={top + 1.2} stroke={INK} strokeWidth="0.2" />
          <text x={px} y={top + 3.6} fontSize="1.6" textAnchor="middle" fill={INK}>{clock(h)}</text>
          <text x={px} y={top + 5.7} fontSize="1.3" textAnchor="middle" fill={MUTED}>{gospelHour(h)}</text>
        </g>
      );
    }
    top += 7;
  }

  // The three days and three nights
  const T = P.three_days;
  if (inRange(T[0].at, T[T.length - 1].end) && span < 400) {
    els.push(
      <text key="three-l" x={M} y={top + 3.6} fontSize="1.9" fontWeight="bold" fill={INK}>3 days, 3 nights</text>
    );
    for (const b of T.filter((b) => inRange(b.at, b.end))) {
      const a = x(b.at);
      const w = Math.max(0.6, x(b.end) - a);
      const night = b.kind === 'night';
      els.push(
        <g key={`three-${b.label}`} onClick={() => onSelect({ ...b, when: when(b.at, b.end) })} style={{ cursor: 'pointer' }}>
          <rect x={a} y={top + 1} width={w} height="4.2" fill={night ? ink('#1e293b') : mono ? '#ffffff' : '#f6e7a8'} stroke={INK} strokeWidth="0.25" opacity={night ? 0.75 : 1} />
          {w > textWidth(b.label, 1.7) + 1 && (
            <text x={a + w / 2} y={top + 3.9} fontSize="1.7" textAnchor="middle" fill={night ? PAPER : INK}>{b.label}</text>
          )}
          <title>{b.note}</title>
        </g>
      );
    }
    top += 7;
  }

  // Tracks of events
  const items = [...P.feasts.map((f) => ({ ...f, track: 'feasts' })), ...P.events]
    .filter((e) => (hourly ? !e.summary : !e.detail))
    .filter((e) => inRange(e.at, e.end ?? e.at))
    .sort((a, b) => (CERTAINTY_RANK[a.certainty] ?? 0) - (CERTAINTY_RANK[b.certainty] ?? 0) || a.at - b.at);
  // Pictures: the events that have one, spread across the sheet, each led down to its marker below
  const pictured = [];
  if (pictures && vignettes.size) {
    const fit = items.filter((e) => vignettes.has(e.id));
    const maxN = Math.floor((R - L + 2) / (CW + 2));
    const picked = fit.length > maxN ? Array.from({ length: maxN }, (_, i) => fit[Math.round((i * (fit.length - 1)) / (maxN - 1))]) : fit;
    const cy = top + 2;
    for (const c of placeCallouts(picked.map((e) => ({ ...e, x: x(e.at) })), CW, L, R)) {
      pictured.push({ ...c, bottom: cy + CH + 6 });
      els.push(
        <g key={`pic-${c.id}`} onClick={() => onSelect({ ...c, when: when(c.at, c.end) })} style={{ cursor: 'pointer' }}>
          <rect x={c.cx - 0.6} y={cy - 0.6} width={CW + 1.2} height={CH + 1.2} fill={PAPER} stroke={INK} strokeWidth="0.35" />
          <svg x={c.cx} y={cy} width={CW} height={CH} viewBox="0 0 240 180" style={mono ? { filter: 'url(#pc-mono)' } : undefined}>
            <use href={`#v-${c.id}`} />
          </svg>
          {wrap2(c.label, CW + 1, 2.1).map((line, k) => (
            <text key={k} x={c.cx + CW / 2} y={cy + CH + 2.8 + k * 2.4} fontSize="2.1" textAnchor="middle" fontWeight="bold" fill={INK}>{line}</text>
          ))}
          <title>{c.label}</title>
        </g>
      );
    }
    if (pictured.length) top = cy + CH + 8;
  }

  let y = top + 2;
  const bottom = H - M - 16;
  let dropped = 0;
  for (const t of TRACKS) {
    const mine = items.filter((e) => e.track === t.id);
    if (!mine.length) continue;
    const later = TRACKS.slice(TRACKS.indexOf(t) + 1).map((u) => Math.min(u.maxRows, items.filter((e) => e.track === u.id).length));
    const reserve = later.reduce((sum, n) => sum + (n ? 8 + n * ROW : 0), 0);
    const roomRows = Math.floor((bottom - y - 8 - reserve) / ROW);
    const laid = mine.map((e) => {
      const a = x(e.at);
      const b = e.end != null ? Math.max(a + 0.8, x(e.end)) : a;
      const tw = textWidth(e.label, SIZE);
      const side = b + 1.6 + tw <= R ? 'right' : a - 1.6 - tw >= M ? 'left' : 'inside';
      const x0 = side === 'left' ? a - 1.6 - tw : side === 'inside' ? b - 1.6 - tw : a - 0.8;
      const x1 = side === 'right' ? b + 1.6 + tw : b + 0.8;
      return { ...e, a, b, tw, side, x0: Math.min(x0, a - 0.8), x1 };
    });
    const { placed, dropped: d } = packRows(laid, Math.max(1, Math.min(t.maxRows, roomRows)), 0.8);
    dropped += d;
    const rows = placed.reduce((m, p) => Math.max(m, p.row + 1), 1);
    els.push(
      <text key={`tl-${t.id}`} x={L} y={y + 2.2} fontSize="2.4" fontWeight="bold" fill={ink(t.color)}>{t.label}</text>
    );
    y += 3.4;
    const ruleY = y;
    els.push(<line key={`tr-${t.id}`} x1={L} x2={R} y1={y} y2={y} stroke={ink(t.color)} strokeWidth="0.3" />);
    for (const p of placed) {
      const py = y + 3 + p.row * ROW;
      const dashed = p.certainty === 'contested';
      const light = p.certainty === 'site-reading';
      const fill = mono ? (light || dashed ? '#ffffff' : INK) : dashed ? PAPER : ink(t.color);
      const pic = pictured.find((c) => c.id === p.id);
      if (pic) {
        els.push(<line key={`lead-${p.id}`} x1={pic.cx + CW / 2} x2={p.a} y1={pic.bottom} y2={ruleY} stroke={INK} strokeWidth="0.2" strokeDasharray="0.8 0.6" />);
        els.push(<circle key={`lead-dot-${p.id}`} cx={p.a} cy={ruleY} r="0.7" fill={INK} />);
      }
      els.push(
        <g key={`ev-${t.id}-${p.id}`} onClick={() => onSelect({ ...p, when: when(p.at, p.end) })} style={{ cursor: 'pointer' }}>
          {p.end != null ? (
            <rect x={p.a} y={py - 1.2} width={p.b - p.a} height="2.4" fill={fill} fillOpacity={light && !mono ? 0.55 : 1} stroke={ink(t.color)} strokeWidth="0.25" strokeDasharray={dashed ? '0.8 0.5' : undefined} />
          ) : (
            <circle cx={p.a} cy={py} r="1.25" fill={fill} fillOpacity={light && !mono ? 0.55 : 1} stroke={ink(t.color)} strokeWidth="0.3" strokeDasharray={dashed ? '0.5 0.4' : undefined} />
          )}
          <text
            x={p.side === 'right' ? p.b + 1.6 : p.side === 'left' ? p.a - 1.6 : p.b - 1.4}
            y={py + 0.85}
            fontSize={SIZE}
            textAnchor={p.side === 'right' ? 'start' : 'end'}
            fill={p.side === 'inside' ? PAPER : INK}
            stroke={p.side === 'inside' ? 'none' : PAPER}
            strokeWidth="0.5"
            style={{ paintOrder: 'stroke' }}
          >
            {p.label}
          </text>
          <title>{p.note}</title>
        </g>
      );
    }
    y += 5 + rows * ROW;
  }
  if (dropped)
    els.push(
      <text key="more" x={R} y={bottom + 2} fontSize="1.8" textAnchor="end" fontStyle="italic" fill={MUTED}>
        {`+${dropped} more: choose a narrower period`}
      </text>
    );

  return (
    <svg
      ref={svgRef}
      className="hc-sheet"
      viewBox={`0 0 ${W} ${H}`}
      style={{ width: '100%', height: 'auto', display: 'block', background: PAPER, boxShadow: '0 1px 6px #0003', fontFamily: SERIF }}
      role="img"
      aria-label={`${period.label}: AD 33, hour by hour`}
    >
      <rect x="0" y="0" width={W} height={H} fill={PAPER} />
      <rect x={M - 3} y={M - 3} width={W - 2 * M + 6} height={H - 2 * M + 6} fill="none" stroke={INK} strokeWidth="0.5" />
      <text x={M} y={M + 5} fontSize="5.4" fontWeight="bold" fill={INK}>{period.label}</text>
      <text x={M} y={M + 10} fontSize="2.7" fill={INK}>
        {`${civilDay(Math.floor(start / 24))} to ${civilDay(Math.floor((end - 1) / 24))}, AD 33: Friday 3 April is Nisan 14, the day of the cross`}
      </text>
      <text x={M} y={M + 14.4} fontSize="2" fill={MUTED}>
        Each Hebrew day runs from about 6 pm to 6 pm, its night shaded. Where the Gospels give the hour an event sits there; elsewhere it keeps the order the text gives and its hour is approximate.
      </text>
      <defs>
        <filter id="pc-mono"><feColorMatrix type="saturate" values="0" /></filter>
      </defs>
      {els}
      <g fontSize="1.9" fill={INK}>
        <text x={M} y={H - M - 7.4}>
          <tspan fontWeight="bold">Solid:</tspan> stated in the text · <tspan fontWeight="bold">pale:</tspan> this site's reading · <tspan fontWeight="bold">dashed:</tspan> placement contested. A bar is a span of time, a dot a moment. Click any entry for its verses.
        </text>
        <text x={M} y={H - M - 4.4} fill={RED}>{`${P.three_days_note.split('. ').slice(0, 2).join('. ')}. This site holds Friday.`}</text>
        <text x={M} y={H - M - 1.4} fill={MUTED}>
          The Gospels count daylight hours from about 6 am (the third hour is about 9 am). the-way.lewy.au/timeline/
        </text>
      </g>
    </svg>
  );
}

export default function PassionChart({ period }) {
  const svgRef = useRef(null);
  const [mono, setMono] = useState(false);
  const [pictures, setPictures] = useState(true);
  const [sprite, setSprite] = useState('');
  useEffect(() => {
    fetch(SPRITES_URL)
      .then((r) => (r.ok ? r.text() : ''))
      .then(setSprite)
      .catch(() => setSprite(''));
  }, []);
  const vignettes = useMemo(
    () => new Set([...sprite.matchAll(/<symbol id="v-([^"]+)"/g)].map((m) => m[1])),
    [sprite]
  );
  const [selected, setSelected] = useState(null);
  const card = {
    padding: '1rem 1.25rem',
    background: theme.cardBg,
    border: `1px solid ${theme.border}`,
    borderRadius: '0.75rem',
    marginBottom: '0.75rem',
  };
  const download = () => {
    const node = svgRef.current;
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
    link.download = `${period.id}.svg`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: sprite }} />
      <div className="hc-controls" style={{ ...card, display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <button style={chip(!mono, '#b45309')} onClick={() => setMono(false)}>Colour</button>
        <button style={chip(mono, '#b45309')} onClick={() => setMono(true)}>Black and white</button>
        <button style={chip(pictures, '#2563eb')} onClick={() => setPictures(!pictures)}>Pictures</button>
        <button style={{ ...chip(false, '#64748b'), marginLeft: 'auto' }} onClick={download}>Download as SVG</button>
        <button style={chip(true, '#be185d')} onClick={() => window.print()}>Print</button>
      </div>
      <div className="hc-sheet-wrap" style={{ marginBottom: '1rem' }}>
        <Sheet period={period} mono={mono} pictures={pictures} vignettes={vignettes} svgRef={svgRef} onSelect={setSelected} />
      </div>
      {selected && (
        <div className="hc-controls" style={{ ...card, display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 18rem' }}>
            <div style={{ fontWeight: 700, fontSize: '1rem' }}>{selected.label}</div>
            <div style={{ fontSize: '0.85rem', color: theme.textMuted, margin: '0.2rem 0 0.5rem' }}>
              {selected.when}
              {selected.refs && ` · ${selected.refs}`}
            </div>
            {selected.note && <p style={{ fontSize: '0.85rem', margin: '0 0 0.5rem' }}>{selected.note}</p>}
            {selected.study_ref && (
              <a href={studyUrl(selected.study_ref.split('#')[0])} style={{ fontSize: '0.85rem' }}>
                Read the study
              </a>
            )}
          </div>
          <button style={chip(false, '#64748b')} onClick={() => setSelected(null)} aria-label="Close">Close</button>
        </div>
      )}
    </div>
  );
}
