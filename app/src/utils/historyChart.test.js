/**
 * Tests for the History Chart's layout. Run with: node --test src/utils/historyChart.test.js
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { CHRONOLOGY, loadEvents } from './chronology.js';
import {
  gregorianTicks,
  makeScale,
  packRows,
  placeCallouts,
  resolveAges,
  resolveKingdoms,
  resolveMovements,
  resolvePeriods,
  resolveThreads,
} from './historyChart.js';

const events = loadEvents();

test('the ages run end to end from Creation, in order, each from a dated event', () => {
  const ages = resolveAges(events);
  assert.equal(ages[0].am, 0);
  for (let i = 1; i < ages.length; i++) {
    assert.ok(ages[i].am > ages[i - 1].am, `${ages[i].id} starts after ${ages[i - 1].id}`);
    assert.equal(ages[i - 1].amEnd, ages[i].am, `${ages[i - 1].id} ends where ${ages[i].id} starts`);
  }
  assert.equal(ages.at(-1).amEnd, Infinity, 'the new creation has no end');
});

test('the ages follow the epoch: the Flood age starts at the Flood, the church at AD 33', () => {
  const ages = Object.fromEntries(resolveAges(events).map((a) => [a.id, a]));
  assert.equal(ages.postdiluvian.am, 1656);
  assert.equal(ages.church.am, events.find((e) => e.id === 'anchor_41').am);
});

test('the periods run in order, the exile from the temple burned to Cyrus', () => {
  const periods = resolvePeriods(events);
  for (const p of periods) assert.ok(p.amEnd > p.am, `${p.id} has a length`);
  for (let i = 1; i < periods.length; i++) assert.ok(periods[i].am >= periods[i - 1].am);
  const exile = periods.find((p) => p.id === 'exile');
  assert.equal(exile.amEnd - exile.am, 586 - 538);
});

test('each deportation is followed in time by a return', () => {
  const moves = resolveMovements(events);
  const lastOut = Math.max(...moves.filter((m) => m.direction === 'out').map((m) => m.am));
  const firstBack = Math.min(...moves.filter((m) => m.direction === 'back').map((m) => m.am));
  assert.ok(firstBack > lastOut);
  assert.equal(moves.find((m) => m.event === 'anchor_12').gregorian_year, -586);
});

test("Daniel's kingdoms follow one another without a gap until the future ones", () => {
  const ks = resolveKingdoms(events);
  const dated = ks.filter((k) => !k.future && k.id !== 'stone');
  for (let i = 1; i < dated.length; i++) assert.equal(dated[i].am, dated[i - 1].amEnd, `${dated[i].id} follows ${dated[i - 1].id}`);
  assert.deepEqual(dated.map((k) => k.gStart), [-605, -539, -331, -63]);
  assert.equal(ks.find((k) => k.id === 'rome').certainty, 'site-reading', 'Daniel never names the fourth kingdom');
});

test('every thread event is a dated event, so no thread silently loses a point', () => {
  for (const t of resolveThreads(events)) {
    assert.deepEqual(t.missing, [], `${t.id} names undated or unknown events`);
    const ams = t.points.map((p) => p.am);
    assert.deepEqual(ams, [...ams].sort((p, q) => p - q), `${t.id} runs forward in time`);
  }
});

test('artifacts store one calendar and load with both, ranges included', () => {
  for (const a of CHRONOLOGY.artifacts) {
    assert.equal(a.am_year, undefined, `${a.id} stores no Anno Mundi year`);
    if (a.gregorian_end != null) assert.ok(a.gregorian_end > a.gregorian_year, `${a.id} range runs forward`);
  }
  const dss = events.find((e) => e.id === 'dead_sea_scrolls');
  assert.equal(dss.source, 'artifact');
  assert.ok(dss.am_end > dss.am);
});

test('a fitted scale still covers the sheet exactly and never runs backwards', () => {
  const ams = events.filter((e) => e.am != null).map((e) => e.am);
  const s = makeScale(0, 7400, 30, 290, 'fitted', ams);
  assert.equal(s.x(0), 30);
  assert.ok(Math.abs(s.x(7400) - 290) < 1e-9);
  for (let am = 0; am < 7400; am += 37) assert.ok(s.x(am + 37) >= s.x(am));
  assert.ok(s.segments.length > 1, 'the whole week folds somewhere');
  const crowded = s.segments.find((sg) => sg.am0 <= 3900 && sg.am1 > 3900);
  const empty = s.segments.find((sg) => sg.am0 <= 6500 && sg.am1 > 6500);
  assert.ok(crowded.yearsPerCm < empty.yearsPerCm, 'the years around Christ open out');
});

test('BC/AD ticks skip the year zero that does not exist', () => {
  const s = makeScale(3900, 4000, 30, 290);
  const ticks = gregorianTicks(s.segments);
  assert.ok(!ticks.some((t) => t.g === 0));
  assert.ok(ticks.some((t) => t.g === -50) && ticks.some((t) => t.g === 10));
});

test('packed labels never overlap in a row, and what cannot fit is counted', () => {
  const items = Array.from({ length: 10 }, (_, i) => ({ id: i, x0: i * 2, x1: i * 2 + 10 }));
  const { placed, dropped } = packRows(items, 3);
  assert.equal(placed.length + dropped, 10);
  for (const p of placed)
    for (const q of placed)
      if (p !== q && p.row === q.row) assert.ok(p.x1 <= q.x0 || q.x1 <= p.x0);
});

test('pictures keep inside the sheet and apart from one another', () => {
  const items = [10, 12, 14, 280].map((x, i) => ({ id: i, x }));
  const placed = placeCallouts(items, 26, 30, 290);
  for (const p of placed) assert.ok(p.cx >= 30 && p.cx + 26 <= 290);
  const xs = placed.map((p) => p.cx).sort((p, q) => p - q);
  for (let i = 1; i < xs.length; i++) assert.ok(xs[i] - xs[i - 1] >= 26);
});
