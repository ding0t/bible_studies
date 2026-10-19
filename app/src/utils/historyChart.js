/**
 * Layout for the History Chart: printable A4 sheets of the chronology, drawn by
 * components/chronology/HistoryChart.jsx. Everything here is plain arithmetic on the shared event
 * list (chronology.js loadEvents), so a sheet's content is decided in one place and tested in
 * historyChart.test.js. Units are millimetres on an A4 landscape sheet.
 */
import { CHRONOLOGY, gregorianToAm, amToGregorian } from './chronology.js';

export const SHEET = { w: 297, h: 210, margin: 8 };
const EPOCH = 'genealogy';

// A span starts at a dated event and runs to the next span's start, or to its own `to` event.
function resolveSpans(list, events, kind) {
  const byId = new Map(events.map((e) => [e.id, e]));
  const amOf = (id) => {
    const am = byId.get(id)?.am;
    if (am == null) throw new Error(`${kind}: no dated event ${id}`);
    return am;
  };
  const starts = list.map((s) => ({ ...s, am: s.from_am ?? amOf(s.from) }));
  return starts.map((s, i) => ({
    ...s,
    amEnd: s.to ? amOf(s.to) : (starts[i + 1]?.am ?? Infinity),
  }));
}

/** The ages (chronology.json `ages`) with their start and end on the Anno Mundi axis. */
export const resolveAges = (events) => resolveSpans(CHRONOLOGY.ages, events, 'age');

/** The periods inside the ages (chronology.json `periods`): In Egypt, the divided kingdom, the exile. */
export const resolvePeriods = (events) => resolveSpans(CHRONOLOGY.periods, events, 'period');

/** The exiles and returns (chronology.json `movements`), each placed at its event's year. */
export function resolveMovements(events) {
  const byId = new Map(events.map((e) => [e.id, e]));
  return CHRONOLOGY.movements.map((m) => {
    const e = byId.get(m.event);
    if (e?.am == null) throw new Error(`movement: no dated event ${m.event}`);
    return { ...m, id: `move-${m.event}`, am: e.am, gregorian_year: e.gregorian, source: 'movement' };
  });
}

/** Threads (chronology.json `threads`) with each event resolved; undated or unknown ids listed. */
export function resolveThreads(events) {
  const byId = new Map(events.map((e) => [e.id, e]));
  return CHRONOLOGY.threads.map((t) => {
    const points = [];
    const missing = [];
    for (const id of t.events) {
      const e = byId.get(id);
      if (e?.am != null) points.push({ id, am: e.am, label: e.label });
      else missing.push(id);
    }
    return { ...t, points, missing };
  });
}

/** Split a range into n equal sheets, in order. */
export function splitSheets(amStart, amEnd, n) {
  const step = (amEnd - amStart) / n;
  return Array.from({ length: n }, (_, i) => [amStart + i * step, amStart + (i + 1) * step]);
}

/**
 * How much of the sheet each stretch of years gets. 'even' is one scale throughout. 'fitted' gives
 * each of `bins` equal stretches a width that grows with the square root of the events in it, so a
 * crowded century opens out and an empty millennium closes up; the sheet says so with a fold at
 * every change of scale and the years per centimetre of each stretch.
 */
export function makeScale(amStart, amEnd, x0, x1, mode = 'even', ams = [], bins = 24) {
  const span = amEnd - amStart;
  if (mode !== 'fitted') {
    const k = (x1 - x0) / span;
    return {
      x: (am) => x0 + (am - amStart) * k,
      segments: [{ am0: amStart, am1: amEnd, x0, x1, yearsPerCm: 10 / k }],
    };
  }
  const counts = new Array(bins).fill(0);
  for (const am of ams) {
    if (am < amStart || am > amEnd) continue;
    counts[Math.min(bins - 1, Math.floor(((am - amStart) / span) * bins))]++;
  }
  const weights = counts.map((c) => 1 + 1.6 * Math.sqrt(c));
  const total = weights.reduce((a, b) => a + b, 0);
  const edges = [x0];
  for (const w of weights) edges.push(edges[edges.length - 1] + ((x1 - x0) * w) / total);
  const binSpan = span / bins;
  const x = (am) => {
    if (am >= amEnd) return x1;
    const t = Math.max(0, (am - amStart) / binSpan);
    const i = Math.floor(t);
    return edges[i] + (edges[i + 1] - edges[i]) * (t - i);
  };
  // Neighbouring stretches within 1.7 times each other's scale read as one; only a change a reader
  // would notice earns a fold.
  const segments = [];
  for (let i = 0; i < bins; i++) {
    const ypc = (binSpan / (edges[i + 1] - edges[i])) * 10;
    const last = segments[segments.length - 1];
    if (last && Math.max(ypc, last.yearsPerCm) / Math.min(ypc, last.yearsPerCm) < 1.7) {
      last.am1 = amStart + (i + 1) * binSpan;
      last.x1 = edges[i + 1];
      last.yearsPerCm = ((last.am1 - last.am0) / (last.x1 - last.x0)) * 10;
    } else {
      segments.push({
        am0: amStart + i * binSpan,
        am1: amStart + (i + 1) * binSpan,
        x0: edges[i],
        x1: edges[i + 1],
        yearsPerCm: ypc,
      });
    }
  }
  return { x, segments };
}

const STEPS = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000];
function step(span, widthMm, minGapMm) {
  const target = Math.max(1, widthMm / minGapMm);
  return STEPS.find((s) => span / s <= target) ?? 1000;
}

/** Anno Mundi ticks, at a round step chosen per scale segment so labels never crowd. */
export function amTicks(segments, minGapMm = 16) {
  const out = [];
  for (const sg of segments) {
    const s = step(sg.am1 - sg.am0, sg.x1 - sg.x0, minGapMm);
    for (let am = Math.ceil(sg.am0 / s) * s; am < sg.am1; am += s) out.push(am);
  }
  return [...new Set(out)];
}

/** Gregorian ticks (BC/AD round numbers, no year zero), each returned with its Anno Mundi place. */
export function gregorianTicks(segments, minGapMm = 16) {
  const out = [];
  for (const sg of segments) {
    const g0 = amToGregorian(sg.am0, EPOCH);
    const g1 = amToGregorian(sg.am1, EPOCH);
    const s = step(g1 - g0, sg.x1 - sg.x0, minGapMm);
    for (let g = Math.ceil(g0 / s) * s; g < g1; g += s) {
      if (g === 0) continue;
      out.push({ g, am: gregorianToAm(g, EPOCH) });
    }
  }
  return out;
}

export function formatYear(g) {
  return g < 0 ? `${-g} BC` : `AD ${g}`;
}

/** A label's width in mm at a font size in mm, close enough for packing Georgia and Helvetica. */
export const textWidth = (s, size) => String(s).length * size * 0.5;

/**
 * Stack labelled items into rows, nearest the baseline first, so no two overlap. Items come in
 * priority order; one that cannot find a row within maxRows is dropped and counted, so a crowded
 * sheet keeps its most important entries and says how many it left out.
 */
export function packRows(items, maxRows, gap = 1.2) {
  const placed = [];
  let dropped = 0;
  const rows = [];
  for (const it of items) {
    let row = -1;
    for (let r = 0; r < maxRows; r++) {
      const taken = rows[r] ?? [];
      if (taken.every(([a, b]) => it.x1 + gap <= a || it.x0 >= b + gap)) {
        row = r;
        break;
      }
    }
    if (row === -1) {
      dropped++;
      continue;
    }
    (rows[row] ??= []).push([it.x0, it.x1]);
    placed.push({ ...it, row });
  }
  return { placed, dropped };
}

/**
 * Pictures sit in a row above their events, each as near its own year as the others allow: pushed
 * right past the one before, then pulled back left from the sheet's edge. Pictures that cannot fit
 * at all are dropped from the right-hand end of the priority order (caller sorts by priority).
 */
export function placeCallouts(items, w, left, right, gap = 2) {
  const maxN = Math.floor((right - left + gap) / (w + gap));
  const kept = items.slice(0, maxN).sort((a, b) => a.x - b.x);
  const xs = kept.map((it) => Math.max(left, Math.min(right - w, it.x - w / 2)));
  for (let i = 1; i < xs.length; i++) xs[i] = Math.max(xs[i], xs[i - 1] + w + gap);
  for (let i = xs.length - 1; i >= 0; i--) {
    const limit = i === xs.length - 1 ? right - w : xs[i + 1] - w - gap;
    xs[i] = Math.min(xs[i], limit);
  }
  return kept.map((it, i) => ({ ...it, cx: xs[i] }));
}

/**
 * Which people a sheet has room for: everyone in a short span, the lineage's main figures in a
 * long one. significance_level 1 is the line from Adam to Jesus that every summary names.
 */
export function peopleLevel(yearsOnSheet) {
  if (yearsOnSheet > 2500) return 1;
  if (yearsOnSheet > 900) return 2;
  return 3;
}

/** The year now, on the Anno Mundi axis: the chart marks where the reader stands. */
export function presentAm(now = new Date()) {
  return gregorianToAm(now.getFullYear(), EPOCH);
}
