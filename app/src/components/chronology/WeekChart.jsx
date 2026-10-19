import React, { useEffect, useMemo, useRef, useState } from 'react';
import { CHRONOLOGY } from '../../utils/chronology';
import { SHEET, packRows, placeCallouts, textWidth } from '../../utils/historyChart';
import { CERTAINTY_META, chip, studyUrl, theme } from './shared';

// The printable chart for Daniel's seventieth week: seven years of 360 days counted from the covenant
// of Daniel 9:27, drawn from the same future_sequence the Timeline reads. A picture over the years for
// each scene Scripture describes, three lanes under them (heaven, the earth, Israel), the midpoint ruled
// across all three, and the spans the text counts underneath. The week is undated (Mark 13:32), so its
// axis is years from the covenant and carries no calendar year.
const SPRITES_URL = '/assets/chart/sprites.svg';
const SERIF = "Georgia, 'Times New Roman', serif";
const INK = '#3b2f1e';
const MUTED = '#6b5a3e';
const PAPER = '#faf6ec';
const RED = '#8b1e1e';
const GOLD = '#e0b24a';
const SIZE = 2.35;
const CW = 29;
const CH = 21.75;

const LANES = [
  { id: 'church', label: 'IN HEAVEN', color: '#9c7a2e', tint: '#f6ecd0' },
  { id: 'earth', label: 'ON THE EARTH', color: '#8b3a1a', tint: '#efe4d0' },
  { id: 'israel', label: 'ISRAEL', color: '#2f4f7f', tint: '#e3e9f2' },
];

// Scenes drawn for the chart, in the order they fall; the eighteen the sheet has room for.
const PICTURES = [
  'rapture', 'covenant', 'lamb_scroll', 'sealed144', 'seals_1_4', 'seal6', 'trumpets_1_6', 'two_witnesses', 'abomination',
  'war_heaven', 'beast_mark', 'wilderness', 'multitude', 'bowls', 'armageddon', 'marriage_of_lamb', 'second_coming', 'look_pierced',
];

const wrap2 = (label, widthMm, size) => {
  const max = Math.floor(widthMm / (size * 0.5));
  if (label.length <= max) return [label];
  const cut = label.lastIndexOf(' ', max);
  const first = cut > 0 ? label.slice(0, cut) : label.slice(0, max);
  const rest = label.slice(first.length).trim();
  return [first, rest.length <= max ? rest : `${rest.slice(0, max - 1)}…`];
};

// The three series of judgments, each seventh opening the next seven (Revelation 8:1-2; 11:15; 15:1).
function Cascade({ x, y, mono }) {
  const sealFill = ['#f7f4ea', '#a8322d', '#2b2622', '#a3ad92', '#8b1e1e', '#8b1e1e', '#8b1e1e'];
  const glyph = (kind, i, gx) => {
    const cy = y + 4;
    if (kind === 'seal') {
      const pts = Array.from({ length: 24 }, (_, k) => {
        const r = k % 2 === 0 ? 2.2 : 1.9;
        const a = (Math.PI * 2 * k) / 24;
        return `${gx + r * Math.cos(a)} ${cy + r * Math.sin(a)}`;
      });
      return <path key={`s${i}`} d={`M${pts.join(' L')} Z`} fill={mono ? '#fff' : sealFill[i]} stroke={INK} strokeWidth="0.25" />;
    }
    if (kind === 'trumpet') {
      return <path key={`t${i}`} d={`M${gx - 2} ${cy + 0.4} L${gx + 0.6} ${cy - 0.3} L${gx + 2} ${cy - 1.5} L${gx + 2} ${cy + 1.5} L${gx + 0.6} ${cy + 0.7} Z`} fill={mono ? '#fff' : GOLD} stroke={INK} strokeWidth="0.25" />;
    }
    return <path key={`b${i}`} d={`M${gx - 2} ${cy - 0.8} H${gx + 2} A2 1.9 0 0 1 ${gx - 2} ${cy - 0.8} Z`} fill={mono ? '#fff' : '#b3392d'} stroke={INK} strokeWidth="0.25" />;
  };
  return (
    <g>
      <text x={x} y={y - 1} fontSize="2.2" fontWeight="bold" fill={INK}>Each seventh opens the next seven</text>
      {['seal', 'trumpet', 'bowl'].map((kind, row) => (
        <g key={kind}>
          {Array.from({ length: 7 }, (_, i) => glyph(kind, i, x + 3 + row * 31 + i * 4.2))}
          <text x={x + 3 + row * 31} y={y + 10} fontSize="1.8" fill={MUTED}>{['7 seals', '7 trumpets', '7 bowls'][row]}</text>
          {row < 2 && <path d={`M${x + 3 + row * 31 + 28.6} ${y + 4} h2.4 l-1.2 -1.1 m1.2 1.1 l-1.2 1.1`} stroke={RED} strokeWidth="0.4" fill="none" />}
        </g>
      ))}
    </g>
  );
}

export function Sheet({ period, mono, pictures, vignettes, svgRef, onSelect }) {
  const { w: W, h: H, margin: M } = SHEET;
  const [start, end] = period.future;
  const L = M + 21;
  const R = W - M - 2;
  const x = (yr) => L + ((Math.min(Math.max(yr, start), end) - start) / (end - start)) * (R - L);
  const ink = (c) => (mono ? INK : c);
  const events = CHRONOLOGY.future_sequence.events.filter((e) => e.at <= end && (e.end ?? e.at) >= start);
  const els = [];

  // --- picture band: eighteen scenes over the years, two rows, each led down to its place on the axis
  const rowH = CH + 7.2;
  const picTop = 25;
  const axisTop = picTop + rowH * 2 + 3;
  const anchor = (e) => (e.end != null && e.end - e.at < 100 ? (e.at + e.end) / 2 : e.at);
  const placed = [];
  if (pictures && vignettes.size) {
    const fit = PICTURES.map((id) => events.find((e) => e.id === id)).filter((e) => e && vignettes.has(e.id));
    const sorted = fit.map((e) => ({ ...e, px: x(anchor(e)) })).sort((a, b) => a.px - b.px);
    const rowsOf = [sorted.filter((_, i) => i % 2 === 0), sorted.filter((_, i) => i % 2 === 1)];
    rowsOf.forEach((row, r) => {
      const cy = picTop + r * rowH;
      for (const c of placeCallouts(row.map((e) => ({ ...e, x: e.px })), CW, L - 12, R + 4, 1.6)) {
        placed.push({ ...c, cy });
      }
    });
    for (const c of placed) {
      els.push(<line key={`lead-${c.id}`} x1={c.cx + CW / 2} x2={c.px} y1={c.cy + CH + 6.4} y2={axisTop} stroke={INK} strokeWidth="0.2" strokeDasharray="0.8 0.6" />);
    }
    for (const c of placed) {
      els.push(
        <g key={`pic-${c.id}`} onClick={() => onSelect(c)} style={{ cursor: 'pointer' }}>
          <rect x={c.cx - 0.5} y={c.cy - 0.5} width={CW + 1} height={CH + 1} fill={PAPER} stroke={INK} strokeWidth="0.35" strokeDasharray={c.certainty === 'contested' ? '1.1 0.6' : undefined} />
          <svg x={c.cx} y={c.cy} width={CW} height={CH} viewBox="0 0 240 180" style={mono ? { filter: 'url(#wk-mono)' } : undefined}>
            <use href={`#v-${c.id}`} />
          </svg>
          {wrap2(c.label, CW + 3, 1.9).map((line, k) => (
            <text key={k} x={c.cx + CW / 2} y={c.cy + CH + 2.8 + k * 2.2} fontSize="1.9" textAnchor="middle" fontWeight="bold" fill={INK}>{line}</text>
          ))}
          <title>{c.label}</title>
        </g>
      );
    }
  }
  const top = pictures && placed.length ? axisTop : picTop + 3;

  // --- the year axis
  const bandH = 6.4;
  for (let i = 0; i < 7; i++) {
    els.push(<rect key={`yr-${i}`} x={x(i)} y={top} width={x(i + 1) - x(i)} height={bandH} fill={i % 2 ? '#e9dfc6' : '#f3ead3'} stroke={INK} strokeWidth="0.2" />);
    els.push(<text key={`yl-${i}`} x={x(i) + 1.6} y={top + 4.3} fontSize="2.6" fontWeight="bold" fill={INK}>{`Year ${i + 1}`}</text>);
  }
  els.push(<text key="pre" x={x(start) + 1} y={top + 4.3} fontSize="2" fill={MUTED} fontStyle="italic">the church age</text>);
  els.push(<text key="post" x={x(7) + 1.4} y={top + 4.3} fontSize="2" fill={MUTED} fontStyle="italic">the King comes</text>);
  for (let i = 0; i <= 7; i++) {
    els.push(<text key={`dl-${i}`} x={x(i)} y={top + bandH + 2.6} fontSize="1.7" textAnchor="middle" fill={MUTED}>{i === 0 ? 'day 0' : (i * 360).toLocaleString()}</text>);
  }
  els.push(<text key="dmid" x={x(3.5) + 1} y={top + bandH + 2.6} fontSize="1.9" fontWeight="bold" fill={RED}>1,260</text>);

  // --- the lanes
  let y = top + bandH + 4.6;
  const laneTop = y;
  const laidOut = LANES.map((lane) => {
    const mine = events.filter((e) => e.track === lane.id);
    const laid = mine.map((e) => {
      const a = x(e.at);
      const bar = e.end != null && e.end - e.at < 100;
      const b = bar ? Math.max(a + 0.8, x(e.end)) : a;
      const open = e.end != null && !bar;
      const tw = textWidth(e.label, SIZE);
      const side = b + 1.6 + tw <= R ? 'right' : a - 1.6 - tw >= L - 4 ? 'left' : 'inside';
      const x0 = side === 'left' ? a - 1.6 - tw : side === 'inside' ? b - 1.6 - tw : a - 0.8;
      const x1 = side === 'right' ? b + 1.6 + tw : b + 0.8;
      return { ...e, a, b: open ? R : b, bar: bar || open, open, tw, side, x0: Math.min(x0, a - 0.8), x1 };
    });
    return { lane, laid };
  });
  const avail = 176 - laneTop;
  const maxRows = 10;
  const packs = laidOut.map(({ laid }) => packRows(laid.sort((p, q) => (p.certainty === 'stated' ? 0 : 1) - (q.certainty === 'stated' ? 0 : 1) || p.at - q.at), maxRows, 0.8));
  const rowsPer = packs.map((p) => Math.max(1, p.placed.reduce((m, q) => Math.max(m, q.row + 1), 1)));
  const ROW = Math.min(4.6, (avail - 3 * 3) / rowsPer.reduce((a, b) => a + b, 0));
  let dropped = 0;
  laidOut.forEach(({ lane }, li) => {
    const h = rowsPer[li] * ROW + 3;
    els.push(<rect key={`lane-${lane.id}`} x={L - 1} y={y} width={R - L + 3} height={h} fill={mono ? '#f4f0e6' : lane.tint} />);
    els.push(<text key={`ln-${lane.id}`} x={M} y={y + 4.6} fontSize="2.5" fontWeight="bold" fill={ink(lane.color)}>{lane.label}</text>);
    dropped += packs[li].dropped;
    for (const p of packs[li].placed) {
      const py = y + 3.2 + p.row * ROW;
      const st = CERTAINTY_META[p.certainty] ?? CERTAINTY_META.stated;
      const dashed = p.certainty === 'contested';
      const light = p.certainty === 'site-reading';
      const fill = mono ? (light || dashed ? '#ffffff' : INK) : dashed ? PAPER : ink(lane.color);
      const mark = p.bar ? (
        <g>
          <rect x={p.a} y={py - 1} width={Math.max(0.8, p.b - p.a)} height="2" fill={fill} fillOpacity={light && !mono ? 0.55 : 1} stroke={ink(lane.color)} strokeWidth="0.25" strokeDasharray={dashed ? '0.8 0.5' : undefined} />
          {p.open && <path d={`M${R - 1.2} ${py - 1.6} L${R + 1} ${py} L${R - 1.2} ${py + 1.6}`} fill="none" stroke={ink(lane.color)} strokeWidth="0.4" />}
        </g>
      ) : (
        <circle cx={p.a} cy={py} r="1.2" fill={fill} fillOpacity={light && !mono ? 0.55 : 1} stroke={ink(lane.color)} strokeWidth="0.3" strokeDasharray={dashed ? '0.5 0.4' : undefined} />
      );
      els.push(
        <g key={`ev-${p.id}`} onClick={() => onSelect(p)} style={{ cursor: 'pointer' }}>
          {mark}
          <text
            x={p.side === 'right' ? p.b + 1.6 : p.side === 'left' ? p.a - 1.6 : p.b - 1.4}
            y={py + 0.8}
            fontSize={SIZE}
            textAnchor={p.side === 'right' ? 'start' : 'end'}
            fill={p.side === 'inside' && !dashed && !light ? PAPER : INK}
            stroke={p.side === 'inside' && !dashed && !light ? 'none' : PAPER}
            strokeWidth="0.5"
            style={{ paintOrder: 'stroke' }}
          >
            {p.label}
          </text>
          <title>{`${p.label} (${p.refs}) · ${st.label}`}</title>
        </g>
      );
    }
    y += h + 1.2;
  });
  const laneBottom = y - 1.2;

  // The midpoint, ruled across the picture band's axis and all three lanes (Daniel 9:27).
  els.push(<line key="mid" x1={x(3.5)} x2={x(3.5)} y1={top} y2={laneBottom} stroke={RED} strokeWidth="0.7" />);
  els.push(<rect key="midtag" x={x(3.5) - 21} y={laneBottom + 0.6} width="42" height="3.8" rx="0.8" fill={RED} />);
  els.push(<text key="midtxt" x={x(3.5)} y={laneBottom + 3.3} fontSize="2" fontWeight="bold" textAnchor="middle" fill={PAPER}>THE MIDPOINT · DANIEL 9:27</text>);

  // --- the spans the text counts, drawn to the axis's own scale
  const sy = laneBottom + 8.4;
  const span = (a, b, label, ref, dashed, row, inline) => (
    <g key={`sp-${label}`}>
      <path d={`M${x(a)} ${sy + row * 5} H${x(b)}`} stroke={RED} strokeWidth="0.6" strokeDasharray={dashed ? '1.6 1' : undefined} />
      <path d={`M${x(a)} ${sy + row * 5 - 1} V${sy + row * 5 + 1} M${x(b)} ${sy + row * 5 - 1} V${sy + row * 5 + 1}`} stroke={RED} strokeWidth="0.5" />
      {inline ? (
        <text x={x(a) - 1.6} y={sy + row * 5 + 0.8} fontSize="2" fill={RED} textAnchor="end"><tspan fontWeight="bold">{label}</tspan><tspan fill={MUTED} fontStyle="italic">{` ${ref}`}</tspan></text>
      ) : (
        <>
          <text x={(x(a) + x(b)) / 2} y={sy + row * 5 - 1.3} fontSize="2" fontWeight="bold" textAnchor="middle" fill={RED}>{label}</text>
          <text x={(x(a) + x(b)) / 2} y={sy + row * 5 + 2.7} fontSize="1.7" textAnchor="middle" fill={MUTED} fontStyle="italic">{ref}</text>
        </>
      )}
    </g>
  );
  els.push(span(0, 3.5, '1,260 days?', 'the two witnesses: which half, the text does not say (Rev 11:3)', true, 0));
  els.push(span(3.5, 7, '1,260 days · 42 months · a time, times and half a time', 'Rev 12:6; 13:5; 12:14 · Daniel 7:25; 12:7', false, 0));
  els.push(span(3.5, 3.5 + 1290 / 360, '1,290 days', 'from the abomination (Daniel 12:11)', true, 1.7, true));
  els.push(span(3.5, 3.5 + 1335 / 360, '1,335 days', '"Blessed is he who waits" (Daniel 12:12)', true, 2.6, true));

  els.push(<Cascade key="cascade" x={M} y={sy - 0.4} mono={mono} />);
  if (dropped) els.push(<text key="more" x={R} y={laneBottom - 0.4} fontSize="1.8" textAnchor="end" fontStyle="italic" fill={MUTED}>{`+${dropped} more in the Timeline`}</text>);

  return (
    <svg
      ref={svgRef}
      className="hc-sheet"
      viewBox={`0 0 ${W} ${H}`}
      style={{ width: '100%', height: 'auto', display: 'block', background: PAPER, boxShadow: '0 1px 6px #0003', fontFamily: SERIF }}
      role="img"
      aria-label="Daniel's seventieth week, year by year, with a picture for each scene"
    >
      <defs>
        <filter id="wk-mono"><feColorMatrix type="saturate" values="0" /></filter>
      </defs>
      <rect x="0" y="0" width={W} height={H} fill={PAPER} />
      <rect x={M - 3} y={M - 3} width={W - 2 * M + 6} height={H - 2 * M + 6} fill="none" stroke={INK} strokeWidth="0.5" />
      <text x={M} y={M + 5} fontSize="5.4" fontWeight="bold" fill={INK}>Daniel's Seventieth Week</text>
      <text x={M} y={M + 10} fontSize="2.6" fill={INK}>
        Seven years of 360 days from the covenant of Daniel 9:27. Undated: Scripture gives these lengths and keeps the start hidden (Mark 13:32).
      </text>
      <text x={M} y={M + 14} fontSize="2" fill={MUTED}>
        Solid: the text dates it. Pale: this site's reading. Dashed: placed by its order in Revelation, the text does not date it. Click a picture or an entry for its verses.
      </text>
      {els}
      <text x={W - M} y={H - M + 1} fontSize="1.9" textAnchor="end" fill={MUTED}>
        After the manner of Clarence Larkin · the-way.lewy.au/timeline/ · studies: The Tribulation, Immediately After, The Two Witnesses
      </text>
    </svg>
  );
}

export default function WeekChart({ period }) {
  const svgRef = useRef(null);
  const [mono, setMono] = useState(false);
  const [pictures, setPictures] = useState(true);
  const [sprite, setSprite] = useState('');
  const [selected, setSelected] = useState(null);
  useEffect(() => {
    fetch(SPRITES_URL)
      .then((r) => (r.ok ? r.text() : ''))
      .then(setSprite)
      .catch(() => setSprite(''));
  }, []);
  const vignettes = useMemo(() => new Set([...sprite.matchAll(/<symbol id="v-([^"]+)"/g)].map((m) => m[1])), [sprite]);
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
    link.download = 'daniels-seventieth-week.svg';
    link.click();
    URL.revokeObjectURL(url);
  };
  const cert = selected && (CERTAINTY_META[selected.certainty]?.label ?? '');

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
              {selected.refs}
              {cert && ` · ${cert}`}
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
