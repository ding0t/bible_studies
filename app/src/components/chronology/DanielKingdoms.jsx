import React from 'react';
import { gregorianToAm } from '../../utils/chronology';
import { SHEET, formatYear, packRows, resolveKingdoms, resolveMovements, textWidth } from '../../utils/historyChart';

// Daniel's kingdoms on one A4 sheet: Nebuchadnezzar's image is the vertical axis and time runs
// across, so each part of the image rules a line to the years its kingdom held. The axis is to scale
// from the dream to AD 100, breaks for the church age, and ends in the undated future where the feet
// stand and the stone strikes. Drawn from chronology.json `kingdoms` and the shared events.
const EPOCH = 'genealogy';
const SERIF = "Georgia, 'Times New Roman', serif";
const INK = '#3b2f1e';
const MUTED = '#6b5a3e';
const PAPER = '#faf6ec';
const RED = '#8b1e1e';

const METAL = {
  gold: { fill: '#e4bd45', pattern: 'kd-dots' },
  silver: { fill: '#d3d7db', pattern: 'kd-lines' },
  bronze: { fill: '#c4864e', pattern: 'kd-diag' },
  iron: { fill: '#6b7178', pattern: null },
  'iron-clay': { fill: '#8f8575', pattern: 'kd-cross' },
  stone: { fill: '#e7e1d4', pattern: null },
};

// Where each part sits in the statue's own units (utils/build_chart_sprites.py draws it 120 x 320).
const PART_Y = { head: 30, chest: 85, belly: 148, legs: 223, feet: 284, stone: 318 };

export default function DanielKingdoms({ events, mono, onSelect, svgRef }) {
  const { w: W, h: H, margin: M } = SHEET;
  const kingdoms = resolveKingdoms(events);
  const byId = new Map(events.map((e) => [e.id, e]));

  // The statue
  const SX = 12;
  const SW = 50;
  const SY = 26;
  const SH = (SW * 320) / 120;
  const partY = (part) => SY + (PART_Y[part] * SH) / 320;

  // The time axis: to scale from 620 BC to AD 100, a break, then the undated future.
  const T0 = 64;
  const T1 = 212;
  const BREAK = [T1, T1 + 12];
  const F0 = BREAK[1];
  const F1 = W - M;
  const G0 = -620;
  const G1 = 100;
  const span = gregorianToAm(G1, EPOCH) - gregorianToAm(G0, EPOCH);
  const amAt = (g) => gregorianToAm(g, EPOCH);
  const x = (am) => T0 + ((am - amAt(G0)) / span) * (T1 - T0);
  const xg = (g) => x(amAt(g));

  const movements = resolveMovements(events);
  // What Daniel foretold of each kingdom outranks what merely happened in it.
  const DANIEL_SAW = new Set(['anchor_22', 'anchor_23', 'anchor_24', 'anchor_26', 'anchor_28', 'anchor_29', 'anchor_14', 'temple_destroyed_70', 'anchor_41']);
  const rank = (e) => (e.source === 'movement' || DANIEL_SAW.has(e.id) ? 0 : e.core ? 1 : 2);
  const visions = ['daniel_2_dream', 'daniel_7_beasts', 'daniel_8_ram_goat'].map((id) => byId.get(id));
  const dream = visions[0];
  const els = [];
  const metal = (k) => METAL[k.metal] ?? METAL.stone;
  const fillOf = (k) => (mono ? '#ffffff' : metal(k).fill);

  // --- each kingdom: a guide from its part of the image, its label, its years -----------------
  for (const k of kingdoms) {
    if (k.id === 'stone') continue;
    const y = partY(k.part);
    const site = k.certainty !== 'stated';
    const startX = k.future ? F0 + 2 : x(k.am);
    const endX = k.future ? F0 + 30 : x(k.amEnd);
    els.push(
      <line key={`guide-${k.id}`} x1={SX + SW + 1} x2={startX} y1={y} y2={y} stroke={INK} strokeWidth="0.2" strokeDasharray="0.8 0.8" opacity="0.7" />
    );
    const head = k.future
      ? `${k.label} · not dated`
      : `${k.label} · ${formatYear(k.gStart)} to ${formatYear(k.gEnd)}${k.open_end ? ' and on' : ''}`;
    const lines = [
      `Daniel 2: ${k.image} · Daniel 7: ${k.beast}`,
      k.vision ? `Daniel 8: ${k.vision}` : null,
      k.named ? `Named in ${k.named}` : "Not named in Daniel: this site's reading",
    ].filter(Boolean);
    els.push(
      <g key={`label-${k.id}`} onClick={() => onSelect({ ...k, refs: `${k.image_refs}; ${k.beast_refs}` })} style={{ cursor: 'pointer' }}>
        <text x={T0} y={y - 3.2 - lines.length * 2.3} fontSize="2.6" fontWeight="bold" fill={INK}>
          {head}
        </text>
        {lines.map((t, i) => (
          <text key={i} x={T0} y={y - 2.2 - (lines.length - 1 - i) * 2.3} fontSize="1.85" fill={i === lines.length - 1 && site ? RED : MUTED} fontStyle={i === lines.length - 1 ? 'italic' : 'normal'}>
            {t}
          </text>
        ))}
      </g>
    );
    // The bar
    els.push(
      <g key={`bar-${k.id}`} onClick={() => onSelect({ ...k, refs: `${k.image_refs}; ${k.beast_refs}` })} style={{ cursor: 'pointer' }}>
        <rect x={startX} y={y - 1.8} width={Math.max(1, endX - startX)} height="3.6" fill={fillOf(k)} stroke={INK} strokeWidth="0.3" strokeDasharray={site ? '1 0.6' : undefined} />
        {metal(k).pattern && <rect x={startX} y={y - 1.8} width={Math.max(1, endX - startX)} height="3.6" fill={`url(#${metal(k).pattern})`} />}
        {k.open_end && <rect x={endX} y={y - 1.8} width={BREAK[0] - endX} height="3.6" fill="url(#kd-fade-iron)" />}
        <title>{k.note}</title>
      </g>
    );
    // How far ahead it was foretold, from the night of the dream
    if (!k.future && dream) {
      const ahead = k.gStart - dream.gregorian;
      if (ahead > 0) {
        els.push(
          <g key={`ahead-${k.id}`}>
            <path d={`M${xg(dream.gregorian)} ${y} H${startX - 0.8}`} stroke={RED} strokeWidth="0.35" markerEnd="url(#kd-arrow)" />
            <text x={(xg(dream.gregorian) + startX) / 2} y={y + 3.4} fontSize="1.8" textAnchor="middle" fill={RED} fontStyle="italic">
              {`foretold ${ahead} years ahead`}
            </text>
          </g>
        );
      } else {
        els.push(
          <text key={`ahead-${k.id}`} x={endX + 1.2} y={y + 0.7} fontSize="1.8" fill={RED} fontStyle="italic">
            already ruling when the dream was given
          </text>
        );
      }
    }
    // What happened in its years, below the bar
    if (!k.future) {
      // Exiles and returns under their own names, then the anchors Daniel foretold or the core ones.
      const moved = new Set(movements.map((m) => m.event));
      const items = [...movements, ...events.filter((e) => !moved.has(e.id))]
        .filter((e) => ['movement', 'anchor', 'archaeology', 'milestone'].includes(e.source) && e.kind !== 'vision')
        .filter((e) => e.am != null && e.am > k.am && e.am <= k.amEnd)
        .sort((p, q) => rank(p) - rank(q) || p.am - q.am)
        .map((e) => {
          const ex = x(e.am);
          const label = `${e.label} ${formatYear(e.gregorian ?? e.gregorian_year)}`;
          return { ...e, ex, text: label, x0: ex - 0.4, x1: ex + textWidth(label, 1.6) + 0.6 };
        })
        .filter((e) => e.x1 < BREAK[0] + 30);
      // As many rows as fit above the next kingdom's heading.
      const next = kingdoms[kingdoms.indexOf(k) + 1];
      const nextTop = next ? partY(next.part) - 3.2 - 3 * 2.3 - 2 : Infinity;
      const firstRow = y + 5.6 + (dream && k.gStart > dream.gregorian ? 1.6 : 0);
      const { placed } = packRows(items, Math.max(1, Math.min(3, Math.floor((nextTop - firstRow) / 2.3) + 1)), 0.8);
      for (const p of placed) {
        const ly = y + 5.6 + p.row * 2.3 + (dream && k.gStart > dream.gregorian ? 1.6 : 0);
        els.push(
          <g key={`ev-${k.id}-${p.id}`} onClick={() => onSelect(p)} style={{ cursor: 'pointer' }}>
            <line x1={p.ex} x2={p.ex} y1={y + 1.8} y2={ly - 1.4} stroke={INK} strokeWidth="0.15" />
            <text x={p.ex + 0.4} y={ly} fontSize="1.6" fill={INK} stroke={PAPER} strokeWidth="0.4" style={{ paintOrder: 'stroke' }}>
              {p.text}
            </text>
          </g>
        );
      }
    }
  }

  // --- the future: the seventieth week, the stone, the kingdom -------------------------------
  const feetY = partY('feet');
  const stoneK = kingdoms.find((k) => k.id === 'stone');
  const kingdomY = partY('stone') + 6;
  els.push(
    <g key="week70">
      <text x={F0 + 2} y={feetY + 5.4} fontSize="1.8" fill={MUTED} fontStyle="italic">
        Daniel's 70th week · 7 years (Daniel 9:27)
      </text>
    </g>
  );
  els.push(
    <g key="stone" onClick={() => onSelect({ ...stoneK, refs: `${stoneK.image_refs}; ${stoneK.beast_refs}` })} style={{ cursor: 'pointer' }}>
      <path d={`M${F1 - 4} ${feetY - 16} Q${F0 + 40} ${feetY - 14} ${F0 + 33} ${feetY - 2}`} fill="none" stroke={INK} strokeWidth="0.3" strokeDasharray="1 0.8" markerEnd="url(#kd-arrow-ink)" />
      <use href="#stone" x={F1 - 10} y={feetY - 21} width="8" height="8" />
      <text x={F1} y={feetY - 22.5} fontSize="1.85" textAnchor="end" fill={INK} fontStyle="italic">
        a stone cut out by no human hand (Daniel 2:34)
      </text>
      <rect x={F0 + 2} y={kingdomY - 2.4} width={F1 - F0 - 2} height="4.8" fill={mono ? '#ffffff' : '#f6ecd0'} stroke={INK} strokeWidth="0.35" />
      <path d={`M${F1 - 2} ${kingdomY - 3.4} L${F1 + 1.5} ${kingdomY} L${F1 - 2} ${kingdomY + 3.4}`} fill="none" stroke={INK} strokeWidth="0.35" />
      <text x={F0 + 3.5} y={kingdomY + 0.9} fontSize="2.2" fontWeight="bold" fill={INK}>
        The stone becomes a mountain: God's kingdom
      </text>
      <text x={F0 + 2} y={kingdomY + 5.6} fontSize="1.75" fill={MUTED}>
        It shall stand forever (Daniel 2:44) · Christ's reign, Day 7
      </text>
      <title>{stoneK.note}</title>
    </g>
  );
  els.push(
    <g key="kingdom-guide">
      <line x1={SX + SW / 2} x2={F0 + 2} y1={kingdomY} y2={kingdomY} stroke={INK} strokeWidth="0.2" strokeDasharray="0.8 0.8" opacity="0.7" />
      <text x={T0} y={kingdomY - 3} fontSize="2.6" fontWeight="bold" fill={INK}>
        {`${stoneK.label} · not dated`}
      </text>
      <text x={T0} y={kingdomY + 3.6} fontSize="1.85" fill={MUTED}>
        {`Daniel 2: ${stoneK.image} · Daniel 7: ${stoneK.beast}`}
      </text>
    </g>
  );

  // --- the visions: when each was given ------------------------------------------------------
  const visionTop = 22;
  const visionBottom = kingdomY + 8;
  for (const [i, v] of visions.entries()) {
    if (!v) continue;
    const vx = xg(v.gregorian);
    els.push(<line key={`v-${v.id}`} x1={vx} x2={vx} y1={visionTop} y2={visionBottom} stroke={RED} strokeWidth={i ? 0.2 : 0.4} strokeDasharray={i ? '0.6 0.8' : '1.4 0.8'} />);
  }
  if (dream) {
    els.push(
      <g key="v-labels" onClick={() => onSelect(dream)} style={{ cursor: 'pointer' }}>
        <text x={xg(dream.gregorian) + 1} y={visionTop + 0.8} fontSize="2" fontWeight="bold" fill={RED}>
          {`The dream, ${formatYear(dream.gregorian)} (Daniel 2:1)`}
        </text>
        <text x={xg(-551) + 1} y={kingdomY + 8} fontSize="1.7" fill={RED}>
          Daniel 7, c. 553 BC · Daniel 8, c. 551 BC
        </text>
      </g>
    );
  }

  // --- axis: BC/AD to scale, the break, the undated future -----------------------------------
  const AXIS = kingdomY + 12;
  const axis = [<line key="ax" x1={T0} x2={BREAK[0]} y1={AXIS} y2={AXIS} stroke={INK} strokeWidth="0.35" />];
  for (let g = -600; g <= G1; g += 100) {
    const gg = g === 0 ? 1 : g;
    axis.push(
      <g key={`t${g}`}>
        <line x1={xg(gg)} x2={xg(gg)} y1={AXIS} y2={AXIS + 1} stroke={INK} strokeWidth="0.25" />
        <text x={xg(gg)} y={AXIS + 3.4} fontSize="1.9" textAnchor="middle" fill={INK}>{formatYear(gg)}</text>
      </g>
    );
  }
  axis.push(
    <g key="break">
      <path d={`M${BREAK[0]} ${AXIS} l2 -1.4 l2 2.8 l2 -2.8 l2 2.8 l2 -2.8 l2 1.4`} fill="none" stroke={INK} strokeWidth="0.35" />
      <rect x={BREAK[0]} y={visionTop} width={BREAK[1] - BREAK[0]} height={AXIS - visionTop} fill="url(#kd-gap)" />
      <text x={(BREAK[0] + BREAK[1]) / 2} y={(visionTop + AXIS) / 2} fontSize="2" textAnchor="middle" fill={MUTED} fontStyle="italic" transform={`rotate(-90 ${(BREAK[0] + BREAK[1]) / 2} ${(visionTop + AXIS) / 2})`}>
        the church age, between the legs and the feet on this site's reading
      </text>
      <line x1={F0} x2={F1} y1={AXIS} y2={AXIS} stroke={INK} strokeWidth="0.35" strokeDasharray="1.2 0.8" />
      <text x={(F0 + F1) / 2} y={AXIS + 3.4} fontSize="1.9" textAnchor="middle" fill={MUTED} fontStyle="italic">
        not dated (Mark 13:32)
      </text>
    </g>
  );

  return (
    <svg
      ref={svgRef}
      className="hc-sheet"
      viewBox={`0 0 ${W} ${H}`}
      style={{ width: '100%', height: 'auto', display: 'block', background: PAPER, boxShadow: '0 1px 6px #0003', fontFamily: SERIF }}
      role="img"
      aria-label="Daniel's kingdoms: Nebuchadnezzar's image across time"
    >
      <defs>
        <pattern id="kd-dots" width="1.6" height="1.6" patternUnits="userSpaceOnUse"><circle cx="0.8" cy="0.8" r="0.28" fill={INK} opacity="0.55" /></pattern>
        <pattern id="kd-lines" width="1.4" height="1.4" patternUnits="userSpaceOnUse"><path d="M0 0.7 H1.4" stroke={INK} strokeWidth="0.2" opacity="0.55" /></pattern>
        <pattern id="kd-diag" width="1.6" height="1.6" patternUnits="userSpaceOnUse"><path d="M0 1.6 L1.6 0" stroke={INK} strokeWidth="0.22" opacity="0.6" /></pattern>
        <pattern id="kd-cross" width="2" height="2" patternUnits="userSpaceOnUse"><rect width="1" height="1" fill={INK} opacity="0.5" /><rect x="1" y="1" width="1" height="1" fill={INK} opacity="0.5" /></pattern>
        <pattern id="kd-gap" width="1.8" height="1.8" patternUnits="userSpaceOnUse"><path d="M0 1.8 L1.8 0" stroke={INK} strokeWidth="0.12" opacity="0.35" /></pattern>
        <linearGradient id="kd-fade-iron"><stop offset="0" stopColor={mono ? '#999999' : '#6b7178'} stopOpacity="0.9" /><stop offset="1" stopColor={PAPER} stopOpacity="0" /></linearGradient>
        <marker id="kd-arrow" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill={RED} /></marker>
        <marker id="kd-arrow-ink" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill={INK} /></marker>
        <filter id="kd-mono"><feColorMatrix type="saturate" values="0" /></filter>
      </defs>
      <rect x="0" y="0" width={W} height={H} fill={PAPER} />
      <rect x={M - 3} y={M - 3} width={W - 2 * M + 6} height={H - 2 * M + 6} fill="none" stroke={INK} strokeWidth="0.5" />
      <text x={M} y={M + 5} fontSize="5.4" fontWeight="bold" fill={INK}>Daniel's Kingdoms</text>
      <text x={M} y={M + 10} fontSize="2.7" fill={INK}>
        Nebuchadnezzar's image across time: "A great God has made known to the king what shall be after this" (Daniel 2:45, ESV)
      </text>
      <svg x={SX} y={SY} width={SW} height={SH} viewBox="0 0 120 320" style={mono ? { filter: 'url(#kd-mono)' } : undefined}>
        <use href="#statue" />
      </svg>
      {els}
      {axis}
      <g fontSize="1.9" fill={INK}>
        <text x={M} y={H - M - 7.2}>
          <tspan fontWeight="bold">Named by Daniel:</tspan> Babylon (2:38), Media-Persia (8:20), Greece (8:21). Solid bars.
        </text>
        <text x={M} y={H - M - 4.4} fill={RED}>
          <tspan fontWeight="bold">This site's reading:</tspan> Rome as the fourth kingdom; its last form, ten kings and the little horn (the Antichrist), still future; the stone as Christ's thousand-year reign. Dashed bars.
        </text>
        <text x={M} y={H - M - 1.6} fill={MUTED}>
          Daniel 8's little horn is Antiochus IV (175–164 BC), a different figure from Daniel 7's. Click any bar for its verses.
        </text>
      </g>
    </svg>
  );
}
