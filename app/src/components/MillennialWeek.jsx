import React, { useState, useMemo } from 'react';
import {
  CHRONOLOGY,
  amToGregorian,
  gregorianToAm,
  mergePeopleWithVariant,
  loadGenealogyPeople,
  GENEALOGY_INDEX,
} from '../utils/chronology';

const BASE_WIDTH = 1600;
const ROW_HEIGHT = 26;
const MARKER_ROW = 18;
// Wider than this and only the anchor table's core rows show; the rest would sit on top of
// one another between Solomon and Christ.
const CORE_ONLY_SPAN = 3000;
// Narrower than this and each person's recorded events show as their own layer.
const LIFE_EVENTS_SPAN = 600;

// The site works to one chronology line -- the Masoretic numbers on the genealogical epoch
// (Exodus 1446 BC, creation 3959 BC) -- so only that line is on by default. The others stay
// available as comparisons, labelled as such.
const VARIANT_META = {
  mt: { label: 'Masoretic Text (this site)', color: '#2563eb' },
  lxx: { label: 'Septuagint (compare)', color: '#7c3aed' },
  sp: { label: 'Samaritan Pentateuch (compare)', color: '#059669' },
};

const EPOCH_META = {
  genealogy: { color: '#475569' },
  millennial_2075: { color: '#e11d48' },
};

const LAYER_META = {
  genesis: { label: 'Genesis', color: '#b45309' },
  anchor: { label: 'Anchor table', color: '#0891b2' },
  archaeology: { label: 'Other archaeology', color: '#0f766e' },
  milestone: { label: 'Prophecy', color: '#be185d' },
  life: { label: "People's events", color: '#64748b' },
  event: { label: 'Studies', color: '#65a30d' },
};

// Each period is a range on the Anno Mundi axis, given either directly or as Gregorian years
// converted through the primary epoch. The two future periods have no date at all: Scripture gives
// their lengths and withholds their start, so they are drawn on their own undated axis.
const PERIODS = [
  { id: 'week', label: 'The whole week', am: [0, 7000] },
  { id: 'creation-flood', label: 'Creation to the Flood', am: [0, 1700] },
  { id: 'flood-abraham', label: 'Flood to Abraham', am: [1600, 2150] },
  { id: 'patriarchs', label: 'Patriarchs to the conquest', am: [2000, 2600] },
  { id: 'conquest-solomon', label: 'Conquest to Solomon', am: [2530, 3060] },
  { id: 'kingdom-exile', label: 'Kingdom, exile and return', greg: [-1000, -500] },
  { id: 'between', label: 'Between the Testaments', greg: [-540, 5] },
  { id: 'christ', label: 'When Jesus was on earth', greg: [-8, 36] },
  // AD 33, hour by hour: hours from midnight at the start of Saturday 28 March (Julian).
  { id: 'passion-week', label: 'Passion week (AD 33)', dated: [42, 222] },
  { id: 'betrayal', label: 'Thursday night: betrayal and trials', dated: [137, 153] },
  { id: 'crucifixion', label: 'Friday: the crucifixion', dated: [150, 163] },
  { id: 'death-resurrection', label: 'Three days and three nights', dated: [132, 214] },
  { id: 'resurrection', label: 'Sunday: the resurrection', dated: [195, 217] },
  { id: 'pentecost', label: 'Passover to Pentecost', dated: [132, 1404] },
  { id: 'church', label: 'The church age', greg: [25, 2050] },
  { id: 'week70', label: "Daniel's 70th week (undated)", future: [-0.8, 7.6] },
  { id: 'millennium', label: 'The millennium and after (undated)', future: [-15, 1025] },
];

const CERTAINTY_META = {
  stated: { label: 'Stated in the text', opacity: 0.85, dashed: false },
  'site-reading': { label: "This site's reading", opacity: 0.5, dashed: false },
  contested: { label: 'Placement contested', opacity: 0.18, dashed: true },
};

function formatGregorian(year) {
  if (year === null || year === undefined) return 'unknown';
  return year < 0 ? `${Math.abs(year)} BC` : `AD ${year}`;
}

// "1000 BC", "AD 33", "33", "-1000" -> signed Gregorian year (no year zero), or null.
function parseGregorian(text) {
  const t = String(text).trim().toUpperCase();
  const m = t.match(/^(AD\s*)?(-?\d+)\s*(BC|BCE|AD|CE)?$/);
  if (!m) return null;
  let n = parseInt(m[2], 10);
  if (m[3] === 'BC' || m[3] === 'BCE') n = -Math.abs(n);
  return n === 0 ? null : n;
}

function studyUrl(studyRef) {
  return `/${studyRef}/`;
}

function niceStep(span, targetTicks = 14) {
  const steps = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000];
  return steps.find((s) => span / s <= targetTicks) ?? 1000;
}

// Greedy row assignment so overlapping bars on one track do not draw over each other.
function stackRows(items, xOf, minGap = 90) {
  const rowsEnd = [];
  return items.map((it) => {
    const x0 = xOf(it.at);
    const x1 = Math.max(x0 + minGap, xOf(it.end ?? it.at) + 4);
    let row = rowsEnd.findIndex((end) => end <= x0);
    if (row === -1) {
      row = rowsEnd.length;
      rowsEnd.push(x1);
    } else rowsEnd[row] = x1;
    return { ...it, row };
  });
}

// A period can be linked to directly, e.g. /timeline/#christ.
function periodFromHash() {
  if (typeof window === 'undefined') return null;
  const id = window.location.hash.replace('#', '');
  return PERIODS.some((p) => p.id === id) ? id : null;
}

export default function MillennialWeek({ events = [], initialPeriod = null }) {
  const [activeVariants, setActiveVariants] = useState(['mt']);
  const [activeEpochs, setActiveEpochs] = useState(['genealogy']);
  const [layers, setLayers] = useState({
    genealogy: true,
    genesis: true,
    anchor: true,
    archaeology: true,
    milestone: true,
    life: true,
    event: true,
  });
  const [periodId, setPeriodId] = useState(() => initialPeriod ?? periodFromHash() ?? 'week');
  const [custom, setCustom] = useState(null);
  const [fromText, setFromText] = useState('');
  const [toText, setToText] = useState('');
  const [rangeError, setRangeError] = useState('');
  const [zoom, setZoom] = useState(1);
  const [selected, setSelected] = useState(null);

  const genealogyPeople = useMemo(() => loadGenealogyPeople(), []);
  const lineages = GENEALOGY_INDEX.lineages;
  const primaryEpoch = activeEpochs[0] ?? 'genealogy';
  const period = PERIODS.find((p) => p.id === periodId);
  const isFuture = !custom && Boolean(period?.future);
  const isDated = !custom && Boolean(period?.dated);

  const [amStart, amEnd] = useMemo(() => {
    if (custom) return custom;
    if (period.am) return period.am;
    if (period.greg) return period.greg.map((g) => gregorianToAm(g, primaryEpoch));
    return [0, 7000];
  }, [custom, period, primaryEpoch]);
  const span = amEnd - amStart;

  const width = BASE_WIDTH * zoom;
  const amToX = (am) => ((am - amStart) / span) * width;
  const inView = (am, amTo = am) => amTo >= amStart && am <= amEnd;
  const clipX = (am) => amToX(Math.min(Math.max(am, amStart), amEnd));

  const toggleInList = (list, setList, id) => {
    setList(list.includes(id) ? list.filter((x) => x !== id) : [...list, id]);
  };
  const toggleLayer = (id) => setLayers((l) => ({ ...l, [id]: !l[id] }));

  const choosePeriod = (id) => {
    setCustom(null);
    setRangeError('');
    setPeriodId(id);
    setSelected(null);
    if (typeof window !== 'undefined') window.history.replaceState(null, '', `#${id}`);
  };

  const applyCustom = () => {
    const a = parseGregorian(fromText);
    const b = parseGregorian(toText);
    if (a == null || b == null || a >= b) {
      setRangeError('Enter two years, earliest first, e.g. "1000 BC" and "AD 100".');
      return;
    }
    setRangeError('');
    setCustom([gregorianToAm(a, primaryEpoch), gregorianToAm(b, primaryEpoch)]);
    setSelected(null);
  };

  const variantLanes = useMemo(
    () =>
      activeVariants.map((variantId) => ({
        variantId,
        people: mergePeopleWithVariant(genealogyPeople, variantId).filter(
          // == null, not !== null: a person absent from this variant's tradition has undefined
          // year fields rather than null, and undefined slipping through draws a lane bar at
          // NaN coordinates. Cainan son of Arphaxad is LXX-only, so MT and SP hit this.
          (p) => p.gregorian_year_born != null && p.gregorian_year_died != null
        ),
      })),
    [activeVariants, genealogyPeople]
  );

  // Every dated marker, one shape, so the chart rows and the "in view" list read from one source.
  const markers = useMemo(() => {
    const out = [];
    for (const g of CHRONOLOGY.genesis_markers) {
      out.push({ ...g, layer: 'genesis', am: g.am_year, amTo: g.am_end ?? g.am_year });
    }
    for (const a of CHRONOLOGY.anchor_table) {
      out.push({ ...a, layer: 'anchor', am: gregorianToAm(a.gregorian_year, primaryEpoch) });
    }
    for (const a of CHRONOLOGY.anchors) {
      out.push({ ...a, layer: 'archaeology', am: gregorianToAm(a.gregorian_year, primaryEpoch) });
    }
    for (const m of CHRONOLOGY.milestones) {
      out.push({
        ...m,
        layer: 'milestone',
        am: m.am_year ?? gregorianToAm(m.gregorian_year, primaryEpoch),
      });
    }
    for (const e of events || []) {
      if (typeof e.zadok_year === 'number')
        out.push({ ...e, id: e.slug, label: e.title, layer: 'event', am: e.zadok_year });
    }
    const mt = variantLanes.find((l) => l.variantId === 'mt') ?? variantLanes[0];
    for (const p of mt?.people ?? []) {
      for (const [i, ev] of (p.major_events ?? []).entries()) {
        if (typeof ev.zadok_year !== 'number') continue;
        out.push({
          id: `${p.id}-${i}`,
          label: `${p.name}: ${ev.event ?? ev.name ?? ev.description ?? 'event'}`,
          layer: 'life',
          am: ev.zadok_year,
          scripture: ev.scripture ?? ev.reference ?? null,
          note: ev.description ?? null,
        });
      }
    }
    return out
      .map((m) => ({ ...m, amTo: m.amTo ?? m.am }))
      .filter((m) => m.am != null && !Number.isNaN(m.am));
  }, [primaryEpoch, events, variantLanes]);

  const visibleMarkers = useMemo(
    () =>
      markers
        .filter((m) => layers[m.layer])
        .filter((m) => m.layer !== 'anchor' || m.core || span <= CORE_ONLY_SPAN)
        .filter((m) => m.layer !== 'life' || span <= LIFE_EVENTS_SPAN)
        .filter((m) => inView(m.am, m.amTo))
        .sort((a, b) => a.am - b.am),
    [markers, layers, amStart, amEnd]
  );

  // Ticks: on AM hundreds for a wide view, on Gregorian years once the view is narrow enough that
  // a reader thinks in BC/AD.
  const ticks = useMemo(() => {
    const out = [];
    if (span > 1200) {
      const step = niceStep(span);
      for (let am = Math.ceil(amStart / step) * step; am <= amEnd; am += step) out.push(am);
    } else {
      const gStart = amToGregorian(Math.ceil(amStart), primaryEpoch);
      const gEnd = amToGregorian(Math.floor(amEnd), primaryEpoch);
      const step = niceStep(gEnd - gStart);
      for (let g = Math.ceil(gStart / step) * step; g <= gEnd; g += step) {
        out.push(gregorianToAm(g === 0 ? 1 : g, primaryEpoch));
      }
    }
    return [...new Set(out)];
  }, [span, amStart, amEnd, primaryEpoch]);

  const theme = {
    text: 'var(--color-text, #1e293b)',
    textMuted: 'var(--color-text-muted, #64748b)',
    textSubtle: 'var(--color-text-subtle, #475569)',
    bg: 'var(--color-bg, #f8fafc)',
    bgElevated: 'var(--color-bg-elevated, #ffffff)',
    cardBg: 'var(--color-card-bg, #f8fafc)',
    border: 'var(--color-border, #e2e8f0)',
    borderStrong: 'var(--color-border-strong, #cbd5e1)',
    primary: 'var(--color-primary, #3b82f6)',
  };

  const chip = (active, color) => ({
    padding: '0.4rem 0.75rem',
    borderRadius: '999px',
    border: `1.5px solid ${active ? color : theme.border}`,
    background: active ? `${color}1a` : theme.cardBg,
    color: active ? color : theme.textMuted,
    fontWeight: active ? 700 : 500,
    fontSize: '0.8rem',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  });
  const sectionLabel = {
    fontSize: '0.75rem',
    fontWeight: 700,
    color: theme.textMuted,
    marginBottom: '0.4rem',
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

  const markerDate = (m) => {
    if (m.gregorian_year != null) {
      const err = m.error?.startsWith('±') ? ` ${m.error}` : '';
      const range = m.error && /\d-\d/.test(m.error) ? ` (${m.error})` : '';
      return `${formatGregorian(m.gregorian_year)}${err}${range}`;
    }
    const g = formatGregorian(amToGregorian(m.am, primaryEpoch));
    if (m.amTo !== m.am) return `${g} – ${formatGregorian(amToGregorian(m.amTo, primaryEpoch))}`;
    return g;
  };

  const markerRows = ['genesis', 'anchor', 'archaeology', 'milestone', 'life', 'event'].filter(
    (layer) => layers[layer] && (layer !== 'life' || span <= LIFE_EVENTS_SPAN)
  );

  return (
    <div
      style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        color: theme.text,
      }}
    >
      {/* Period presets and custom range */}
      <div
        style={{
          padding: '1rem 1.25rem',
          background: theme.cardBg,
          border: `1px solid ${theme.border}`,
          borderRadius: '0.75rem',
          marginBottom: '0.75rem',
        }}
      >
        <div style={sectionLabel}>PERIOD</div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
          {PERIODS.map((p) => (
            <button
              key={p.id}
              style={chip(!custom && periodId === p.id, p.future ? '#b45309' : '#2563eb')}
              onClick={() => choosePeriod(p.id)}
            >
              {p.label}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: theme.textMuted }}>Or any range:</span>
          <input
            style={input}
            placeholder="1000 BC"
            value={fromText}
            onChange={(e) => setFromText(e.target.value)}
            aria-label="From year"
          />
          <span style={{ fontSize: '0.8rem', color: theme.textMuted }}>to</span>
          <input
            style={input}
            placeholder="AD 100"
            value={toText}
            onChange={(e) => setToText(e.target.value)}
            aria-label="To year"
          />
          <button style={chip(Boolean(custom), '#2563eb')} onClick={applyCustom}>
            Show
          </button>
          {rangeError && <span style={{ fontSize: '0.8rem', color: '#b91c1c' }}>{rangeError}</span>}
        </div>
      </div>

      {isDated ? (
        <DatedSequence
          period={period}
          theme={theme}
          width={width}
          selected={selected}
          setSelected={setSelected}
        />
      ) : isFuture ? (
        <FutureSequence
          period={period}
          theme={theme}
          width={width}
          selected={selected}
          setSelected={setSelected}
        />
      ) : (
        <>
          {/* Controls */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '1.5rem',
              padding: '1rem 1.25rem',
              background: theme.cardBg,
              border: `1px solid ${theme.border}`,
              borderRadius: '0.75rem',
              marginBottom: '1.25rem',
            }}
          >
            <div>
              <div style={sectionLabel}>CHRONOLOGY PATHS</div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {Object.entries(VARIANT_META).map(([id, meta]) => (
                  <button
                    key={id}
                    style={chip(activeVariants.includes(id), meta.color)}
                    onClick={() => toggleInList(activeVariants, setActiveVariants, id)}
                    title={GENEALOGY_INDEX.timeline_variants[id]?.description}
                  >
                    {meta.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div style={sectionLabel}>CREATION EPOCH</div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {CHRONOLOGY.epochs.map((epoch) => (
                  <button
                    key={epoch.id}
                    style={chip(activeEpochs.includes(epoch.id), EPOCH_META[epoch.id].color)}
                    onClick={() => toggleInList(activeEpochs, setActiveEpochs, epoch.id)}
                    title={epoch.note}
                  >
                    {epoch.name} ({formatGregorian(epoch.am0_gregorian)})
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div style={sectionLabel}>LAYERS</div>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button
                  style={chip(layers.genealogy, '#2563eb')}
                  onClick={() => toggleLayer('genealogy')}
                >
                  Lifespans
                </button>
                {Object.entries(LAYER_META).map(([id, meta]) => (
                  <button
                    key={id}
                    style={chip(layers[id], meta.color)}
                    onClick={() => toggleLayer(id)}
                  >
                    {meta.label}
                  </button>
                ))}
              </div>
            </div>

            <div
              style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <button
                style={chip(false, theme.textMuted)}
                onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}
              >
                − Zoom
              </button>
              <span
                style={{
                  fontSize: '0.8rem',
                  color: theme.textMuted,
                  minWidth: '3.5rem',
                  textAlign: 'center',
                }}
              >
                {Math.round(zoom * 100)}%
              </span>
              <button
                style={chip(false, theme.textMuted)}
                onClick={() => setZoom((z) => Math.min(4, z + 0.25))}
              >
                + Zoom
              </button>
            </div>
          </div>

          {/* The chart */}
          <div
            style={{
              overflowX: 'auto',
              background: theme.bgElevated,
              border: `1px solid ${theme.border}`,
              borderRadius: '0.75rem',
              padding: '1rem',
            }}
          >
            <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              {formatGregorian(amToGregorian(Math.round(amStart), primaryEpoch))} –{' '}
              {formatGregorian(amToGregorian(Math.round(amEnd), primaryEpoch))} · AM{' '}
              {Math.round(amStart)}–{Math.round(amEnd)}
              {span > CORE_ONLY_SPAN && layers.anchor && (
                <span style={{ fontWeight: 400, color: theme.textMuted }}>
                  {' '}
                  · showing the anchor table's key rows; pick a period to see all 41
                </span>
              )}
            </div>
            <div style={{ position: 'relative', width: `${width}px` }}>
              {/* Day bands */}
              <div
                style={{
                  position: 'relative',
                  height: '1.6rem',
                  marginBottom: '0.25rem',
                  overflow: 'hidden',
                }}
              >
                {CHRONOLOGY.millennial_days
                  .filter((d) => inView(d.am_start, d.am_end))
                  .map((d) => (
                    <div
                      key={d.day}
                      title={d.label ?? `Day ${d.day}`}
                      style={{
                        position: 'absolute',
                        left: clipX(d.am_start),
                        width: clipX(d.am_end) - clipX(d.am_start),
                        top: 0,
                        bottom: 0,
                        background: d.is_millennial_reign
                          ? 'rgba(217, 119, 6, 0.22)'
                          : d.day % 2
                            ? 'rgba(100,116,139,0.08)'
                            : 'rgba(100,116,139,0.03)',
                        border: d.is_millennial_reign ? '1px solid rgba(217, 119, 6, 0.5)' : 'none',
                        borderRadius: '0.25rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: d.is_millennial_reign ? '#b45309' : theme.textMuted,
                      }}
                    >
                      Day {d.day}
                    </div>
                  ))}
              </div>

              {/* Ruler: AM, with each active epoch's Gregorian reading below */}
              <div
                style={{
                  position: 'relative',
                  height: `${18 + activeEpochs.length * 14}px`,
                  borderBottom: `2px solid ${theme.borderStrong}`,
                  marginBottom: '0.5rem',
                }}
              >
                {ticks.map((am) => (
                  <div
                    key={am}
                    style={{
                      position: 'absolute',
                      left: amToX(am),
                      top: 0,
                      bottom: 0,
                      borderLeft: `1px solid ${theme.border}`,
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        color: theme.textMuted,
                        marginLeft: '2px',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      AM {Math.round(am)}
                    </div>
                    {activeEpochs.map((epochId) => (
                      <div
                        key={epochId}
                        style={{
                          fontSize: '0.6rem',
                          color: EPOCH_META[epochId].color,
                          marginLeft: '2px',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {formatGregorian(amToGregorian(Math.round(am), epochId))}
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              {/* One marker row per layer */}
              {markerRows.map((layer) => (
                <div
                  key={layer}
                  style={{ position: 'relative', height: `${MARKER_ROW}px`, marginBottom: '2px' }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      left: 0,
                      top: 2,
                      fontSize: '0.6rem',
                      color: LAYER_META[layer].color,
                      opacity: 0.7,
                      pointerEvents: 'none',
                    }}
                  >
                    {LAYER_META[layer].label}
                  </div>
                  {visibleMarkers
                    .filter((m) => m.layer === layer)
                    .map((m) => {
                      const color = LAYER_META[layer].color;
                      const isRange = m.amTo !== m.am;
                      const pm = Number((m.error ?? '').replace('±', ''));
                      const errPx =
                        Number.isFinite(pm) && pm > 0 ? amToX(m.am + pm) - amToX(m.am) : 0;
                      return (
                        <button
                          key={`${layer}-${m.id}`}
                          onClick={() => setSelected({ kind: 'marker', ...m })}
                          title={`${m.label} · ${markerDate(m)}`}
                          style={{
                            position: 'absolute',
                            left: isRange ? clipX(m.am) : amToX(m.am) - 5,
                            top: 4,
                            width: isRange ? Math.max(6, clipX(m.amTo) - clipX(m.am)) : 10,
                            height: 10,
                            borderRadius: isRange
                              ? '3px'
                              : m.tier === 'Fixed' || layer !== 'anchor'
                                ? '50%'
                                : '2px',
                            background:
                              m.tier === 'Anchored' || m.tier === 'Bracketed'
                                ? 'transparent'
                                : color,
                            border: `2px solid ${color}`,
                            opacity: isRange ? 0.6 : 1,
                            cursor: 'pointer',
                            padding: 0,
                            boxShadow:
                              errPx > 3
                                ? `-${errPx}px 0 0 -3px ${color}, ${errPx}px 0 0 -3px ${color}`
                                : 'none',
                          }}
                        />
                      );
                    })}
                </div>
              ))}

              {/* Lifespan lanes, one per active variant */}
              {layers.genealogy &&
                variantLanes.map(({ variantId, people }) => (
                  <div key={variantId} style={{ marginTop: '0.5rem', marginBottom: '0.75rem' }}>
                    <div
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: VARIANT_META[variantId].color,
                        marginBottom: '2px',
                      }}
                    >
                      {VARIANT_META[variantId].label}
                    </div>
                    <div style={{ position: 'relative', height: `${ROW_HEIGHT}px` }}>
                      {people
                        .filter((p) => inView(p.zadok_year_born, p.zadok_year_died))
                        .map((p) => {
                          const lineageColor = p.lineages?.includes('jesus_line')
                            ? lineages.jesus_line.color
                            : (lineages.seth_line?.color ?? VARIANT_META[variantId].color);
                          const left = clipX(p.zadok_year_born);
                          const barWidth = Math.max(2, clipX(p.zadok_year_died) - left);
                          return (
                            <div
                              key={p.id}
                              onClick={() => setSelected({ kind: 'person', variantId, ...p })}
                              title={`${p.name}: ${formatGregorian(amToGregorian(p.zadok_year_born, primaryEpoch))} – ${formatGregorian(amToGregorian(p.zadok_year_died, primaryEpoch))} (${p.lifespan_years}y)`}
                              style={{
                                position: 'absolute',
                                left,
                                width: barWidth,
                                top: 4,
                                height: ROW_HEIGHT - 8,
                                background: lineageColor,
                                opacity: 0.75,
                                borderRadius: '2px',
                                cursor: 'pointer',
                                overflow: 'hidden',
                                fontSize: '0.6rem',
                                color: 'white',
                                paddingLeft: '3px',
                                whiteSpace: 'nowrap',
                                lineHeight: `${ROW_HEIGHT - 8}px`,
                              }}
                            >
                              {barWidth > 50 ? p.name : ''}
                            </div>
                          );
                        })}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <DetailPanel
            selected={selected}
            theme={theme}
            activeEpochs={activeEpochs}
            markerDate={markerDate}
          />

          {/* Everything in the current view, as a list: the reliable way to read a crowded stretch */}
          <div style={{ marginTop: '1.25rem' }}>
            <div style={sectionLabel}>IN THIS VIEW ({visibleMarkers.length})</div>
            <div
              style={{
                maxHeight: '22rem',
                overflowY: 'auto',
                border: `1px solid ${theme.border}`,
                borderRadius: '0.5rem',
              }}
            >
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                <tbody>
                  {visibleMarkers.map((m) => (
                    <tr
                      key={`row-${m.layer}-${m.id}`}
                      onClick={() => setSelected({ kind: 'marker', ...m })}
                      style={{ cursor: 'pointer', borderBottom: `1px solid ${theme.border}` }}
                    >
                      <td
                        style={{ padding: '0.3rem 0.5rem', whiteSpace: 'nowrap', fontWeight: 600 }}
                      >
                        {markerDate(m)}
                      </td>
                      <td
                        style={{
                          padding: '0.3rem 0.5rem',
                          whiteSpace: 'nowrap',
                          color: theme.textMuted,
                        }}
                      >
                        AM {Math.round(m.am)}
                      </td>
                      <td style={{ padding: '0.3rem 0.5rem' }}>
                        <span style={{ color: LAYER_META[m.layer].color, fontWeight: 700 }}>●</span>{' '}
                        {m.label}
                        {m.tier && <span style={{ color: theme.textMuted }}> · {m.tier}</span>}
                      </td>
                      <td style={{ padding: '0.3rem 0.5rem', color: theme.textMuted }}>
                        {m.scripture ?? ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <p style={{ fontSize: '0.8rem', color: theme.textMuted, marginTop: '1rem' }}>
            Axis is Anno Mundi (years since creation) — the "a day is a thousand years" frame (2
            Peter 3:8), on this site's chronology: the Masoretic numbers, creation 3959 BC. Pick a
            period or type a range to zoom; filled markers in the anchor table are Fixed, hollow
            ones Anchored or Bracketed, and whiskers show the error bar. Turn on the Septuagint, the
            Samaritan Pentateuch or the dsscalendar.org epoch to compare.
          </p>
        </>
      )}
    </div>
  );
}

function DetailPanel({ selected, theme, activeEpochs, markerDate }) {
  if (!selected) return null;
  return (
    <div
      style={{
        marginTop: '1.25rem',
        background: theme.bgElevated,
        border: `1px solid ${theme.border}`,
        borderRadius: '0.75rem',
        padding: '1.25rem 1.5rem',
      }}
    >
      {selected.kind === 'person' && (
        <>
          <h3 style={{ margin: '0 0 0.25rem 0' }}>{selected.name}</h3>
          <div style={{ fontSize: '0.85rem', color: theme.textMuted, marginBottom: '0.5rem' }}>
            {VARIANT_META[selected.variantId].label} · AM {selected.zadok_year_born}–
            {selected.zadok_year_died} ·{' '}
            {activeEpochs
              .map((e) => `${formatGregorian(amToGregorian(selected.zadok_year_born, e))} (${e})`)
              .join(' / ')}{' '}
            · {selected.lifespan_years} years
          </div>
          {selected.title && <p style={{ margin: 0 }}>{selected.title}</p>}
        </>
      )}
      {selected.kind === 'marker' && (
        <>
          <h3 style={{ margin: '0 0 0.25rem 0' }}>
            {selected.n ? `${selected.n}. ` : ''}
            {selected.label}
          </h3>
          <div style={{ fontSize: '0.85rem', color: theme.textMuted, marginBottom: '0.5rem' }}>
            {markerDate(selected)} · AM {Math.round(selected.am)}
            {selected.tier && ` · ${selected.tier}`}
            {selected.scripture && ` · ${selected.scripture}`}
          </div>
          <p style={{ margin: 0 }}>{selected.evidence ?? selected.note ?? selected.description}</p>
          {(selected.study_ref || selected.url) && (
            <a
              href={selected.url ?? studyUrl(selected.study_ref)}
              style={{ color: theme.primary, fontSize: '0.85rem' }}
            >
              Read the study →
            </a>
          )}
        </>
      )}
      {selected.kind === 'dated' && (
        <>
          <h3 style={{ margin: '0 0 0.25rem 0' }}>{selected.label}</h3>
          <div style={{ fontSize: '0.85rem', color: theme.textMuted, marginBottom: '0.5rem' }}>
            {selected.when} · {selected.refs}
            {selected.timing === 'approx' ? ' · hour placed within the order the text gives' : ''}
          </div>
          <p style={{ margin: 0 }}>{selected.note}</p>
          {selected.study_ref && (
            <a
              href={studyUrl(selected.study_ref)}
              style={{ color: theme.primary, fontSize: '0.85rem' }}
            >
              Read the study →
            </a>
          )}
        </>
      )}
      {selected.kind === 'future' && (
        <>
          <h3 style={{ margin: '0 0 0.25rem 0' }}>{selected.label}</h3>
          <div style={{ fontSize: '0.85rem', color: theme.textMuted, marginBottom: '0.5rem' }}>
            {selected.refs} · {CERTAINTY_META[selected.certainty].label}
          </div>
          <p style={{ margin: 0 }}>{selected.note}</p>
          {selected.study_ref && (
            <a
              href={studyUrl(selected.study_ref)}
              style={{ color: theme.primary, fontSize: '0.85rem' }}
            >
              Read the study →
            </a>
          )}
        </>
      )}
    </div>
  );
}

// The future on its own axis: years of 360 days from the covenant of Daniel 9:27. No Gregorian or
// Anno Mundi year appears here, because Scripture gives these spans without their start.
function FutureSequence({ period, theme, width, selected, setSelected }) {
  const [start, end] = period.future;
  const span = end - start;
  const xOf = (y) => ((Math.min(Math.max(y, start), end) - start) / span) * width;
  const all = CHRONOLOGY.future_sequence.events.filter(
    (e) => (e.end ?? e.at) >= start && e.at <= end
  );
  const tracks = [
    { id: 'church', label: 'The Church, in heaven', color: '#7c3aed' },
    { id: 'earth', label: 'On earth', color: '#b45309' },
  ];
  const step = span > 100 ? 100 : 0.5;
  const ticks = [];
  for (let y = Math.ceil(start / step) * step; y <= end; y += step) ticks.push(y);
  const tickLabel = (y) =>
    span > 100
      ? `Year ${y}`
      : `Year ${y}${y > 0 ? ` · day ${Math.round(y * 360).toLocaleString()}` : ''}`;

  return (
    <>
      <div
        style={{
          padding: '0.9rem 1.1rem',
          marginBottom: '0.75rem',
          border: '1px solid rgba(180, 83, 9, 0.4)',
          background: 'rgba(217, 119, 6, 0.08)',
          borderRadius: '0.75rem',
          fontSize: '0.85rem',
        }}
      >
        <strong>Undated.</strong> Scripture gives these lengths — seven years (Daniel 9:27), 1,260
        days (Revelation 11–13), 1,290 and 1,335 days (Daniel 12:11-12), a thousand years
        (Revelation 20) — and keeps the start hidden (Mark 13:32; Acts 1:7). The axis counts years
        of 360 days from the covenant of Daniel 9:27. The order follows this site's studies; solid
        bars are stated in the text, lighter ones this site's reading, dashed ones placements the
        text leaves open.
      </div>
      <div
        style={{
          overflowX: 'auto',
          background: theme.bgElevated,
          border: `1px solid ${theme.border}`,
          borderRadius: '0.75rem',
          padding: '1rem',
        }}
      >
        <div style={{ position: 'relative', width: `${width}px` }}>
          <div
            style={{
              position: 'relative',
              height: '1.6rem',
              borderBottom: `2px solid ${theme.borderStrong}`,
              marginBottom: '0.5rem',
            }}
          >
            {ticks.map((y) => (
              <div
                key={y}
                style={{
                  position: 'absolute',
                  left: xOf(y),
                  top: 0,
                  bottom: 0,
                  borderLeft: `1px solid ${theme.border}`,
                }}
              >
                <div
                  style={{
                    fontSize: '0.62rem',
                    color: theme.textMuted,
                    marginLeft: '2px',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {tickLabel(y)}
                </div>
              </div>
            ))}
          </div>
          {tracks.map((t) => {
            const items = stackRows(
              all.filter((e) => e.track === t.id).sort((a, b) => a.at - b.at),
              xOf,
              span > 100 ? 120 : 150
            );
            const rows = Math.max(1, ...items.map((i) => i.row + 1));
            return (
              <div key={t.id} style={{ marginBottom: '0.75rem' }}>
                <div
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: t.color,
                    marginBottom: '2px',
                  }}
                >
                  {t.label}
                </div>
                <div style={{ position: 'relative', height: `${rows * 30}px` }}>
                  {items.map((e) => {
                    const c = CERTAINTY_META[e.certainty];
                    const isBar = e.end != null;
                    const left = xOf(e.at);
                    const w = isBar ? Math.max(8, xOf(e.end) - left) : 10;
                    return (
                      <button
                        key={e.id}
                        onClick={() => setSelected({ kind: 'future', ...e })}
                        title={`${e.label} · ${e.refs}`}
                        style={{
                          position: 'absolute',
                          left: isBar ? left : left - 5,
                          top: e.row * 30,
                          height: 22,
                          width: isBar ? w : 'auto',
                          minWidth: 10,
                          padding: '0 6px',
                          borderRadius: '4px',
                          border: `1.5px ${c.dashed ? 'dashed' : 'solid'} ${t.color}`,
                          background: 'transparent',
                          boxShadow: `inset 0 0 0 999px ${t.color}${Math.round(c.opacity * 255)
                            .toString(16)
                            .padStart(2, '0')}`,
                          color: c.opacity > 0.6 ? 'white' : theme.text,
                          fontSize: '0.68rem',
                          textAlign: 'left',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          cursor: 'pointer',
                          outline: selected?.id === e.id ? `2px solid ${theme.primary}` : 'none',
                        }}
                      >
                        {e.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <DetailPanel
        selected={selected?.kind === 'future' ? selected : null}
        theme={theme}
        activeEpochs={[]}
        markerDate={() => ''}
      />
    </>
  );
}

// AD 33, hour by hour: the Hebrew days (sunset to sunset), the appointed times of Leviticus 23 they
// fell on, and the three days and nights as Three Days and Three Nights counts them.
const MONTHS = [
  ['March', 31],
  ['April', 30],
  ['May', 31],
];
const WEEKDAYS = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
// Mark 13:35 names the four Roman night watches: evening, midnight, cockcrow, morning.
const WATCHES = ['evening', 'midnight', 'cockcrow', 'morning'];

function civilDay(dayIndex) {
  let day = 28 + dayIndex;
  let m = 0;
  while (day > MONTHS[m][1]) {
    day -= MONTHS[m][1];
    m += 1;
  }
  return `${WEEKDAYS[dayIndex % 7]} ${day} ${MONTHS[m][0]}`;
}

function clock(hour) {
  const h = Math.round(hour % 24);
  if (h === 0 || h === 24) return 'midnight';
  if (h === 12) return 'noon';
  return h < 12 ? `${h} am` : `${h - 12} pm`;
}

// The Gospels count daylight hours from about 6 am (the third hour is about 9 am) and the night in
// watches of three hours from about 6 pm.
function gospelHour(hour) {
  const h = ((Math.round(hour) % 24) + 24) % 24;
  if (h >= 6 && h < 18) {
    const n = h - 6;
    if (n === 0) return 'daybreak';
    const ord = { 1: '1st', 2: '2nd', 3: '3rd' }[n] ?? `${n}th`;
    return `${ord} hour`;
  }
  const w = Math.floor(((((h - 18) % 24) + 24) % 24) / 3);
  return `${WATCHES[w]} watch`;
}

function DatedSequence({ period, theme, width, selected, setSelected }) {
  const P = CHRONOLOGY.passion_sequence;
  const [start, end] = period.dated;
  const span = end - start;
  const hourly = span <= 48;
  const xOf = (h) => ((Math.min(Math.max(h, start), end) - start) / span) * width;
  const inRange = (a, b = a) => b >= start && a <= end;
  const hebrewOf = (h) => P.days.find((d) => d.start <= h && h < d.end)?.hebrew;
  const when = (h, h2) => {
    const first = `${civilDay(Math.floor(h / 24))}, about ${clock(h)}`;
    const heb = hebrewOf(h);
    if (h2 == null) return `${first}${heb ? ` · ${heb}` : ''}`;
    const sameDay = Math.floor(h / 24) === Math.floor(h2 / 24);
    const second = sameDay ? clock(h2) : `${civilDay(Math.floor(h2 / 24))}, ${clock(h2)}`;
    return `${first} – ${second}${heb ? ` · from ${heb}` : ''}`;
  };
  const pxPerDay = (24 / span) * width;
  const showThree =
    inRange(P.three_days[0].at, P.three_days[P.three_days.length - 1].end) && span < 400;
  const hourStep = hourly ? (width / span >= 60 ? 1 : 2) : 0;
  const hourTicks = [];
  if (hourly)
    for (let h = Math.ceil(start / hourStep) * hourStep; h <= end; h += hourStep) hourTicks.push(h);

  const items = [...P.feasts.map((f) => ({ ...f, track: 'feasts' })), ...P.events]
    .filter((e) => (hourly ? !e.summary : !e.detail))
    .filter((e) => inRange(e.at, e.end ?? e.at));
  const tracks = [
    { id: 'feasts', label: 'Appointed times (Leviticus 23)', color: '#b45309' },
    { id: 'jesus', label: 'Jesus', color: '#2563eb' },
    { id: 'church', label: 'The disciples', color: '#7c3aed' },
  ];
  const choose = (e) => setSelected({ kind: 'dated', ...e, when: when(e.at, e.end) });

  return (
    <>
      <div
        style={{
          padding: '0.9rem 1.1rem',
          marginBottom: '0.75rem',
          border: `1px solid ${theme.border}`,
          background: theme.cardBg,
          borderRadius: '0.75rem',
          fontSize: '0.85rem',
        }}
      >
        <strong>AD 33, on this site's chronology.</strong> Friday 3 April is Nisan 14, the day of
        the cross (
        <a href={studyUrl('last-things/chronology-anchors')} style={{ color: theme.primary }}>
          Chronology Anchors
        </a>
        ). Each Hebrew day runs from about 6 pm to 6 pm, its night shaded. Where the Gospels give
        the hour it is placed there; elsewhere events keep the order the text gives and their hour
        is approximate. The day-and-night count follows{' '}
        <a href={studyUrl('jesus/three-days-and-three-nights')} style={{ color: theme.primary }}>
          Three Days and Three Nights
        </a>
        .
      </div>
      <div
        style={{
          overflowX: 'auto',
          background: theme.bgElevated,
          border: `1px solid ${theme.border}`,
          borderRadius: '0.75rem',
          padding: '1rem',
        }}
      >
        <div style={{ position: 'relative', width: `${width}px` }}>
          {/* Hebrew days, night shaded */}
          <div
            style={{
              position: 'relative',
              height: '2.6rem',
              marginBottom: hourly ? 0 : '0.4rem',
              borderBottom: `2px solid ${theme.borderStrong}`,
            }}
          >
            {P.days
              .filter((d) => inRange(d.start, d.end))
              .map((d) => {
                const left = xOf(d.start);
                const label = pxPerDay > 70 || d.sabbath;
                return (
                  <div
                    key={d.k}
                    style={{
                      position: 'absolute',
                      left,
                      width: xOf(d.end) - left,
                      top: 0,
                      bottom: 0,
                      borderLeft: `1px solid ${theme.borderStrong}`,
                    }}
                  >
                    <div
                      style={{
                        position: 'absolute',
                        left: 0,
                        width: xOf(d.start + 12) - left,
                        top: 0,
                        bottom: 0,
                        background: 'rgba(30, 41, 59, 0.10)',
                      }}
                    />
                    {d.sabbath && (
                      <div
                        style={{
                          position: 'absolute',
                          inset: 0,
                          background: 'rgba(180, 83, 9, 0.08)',
                        }}
                      />
                    )}
                    {label && (
                      <div
                        style={{
                          position: 'sticky',
                          left: 0,
                          fontSize: '0.62rem',
                          padding: '1px 3px',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        <div style={{ fontWeight: 700 }}>
                          {d.hebrew}
                          {d.sabbath ? ' · Sabbath' : ''}
                        </div>
                        <div style={{ color: theme.textMuted }}>daylight: {d.daylight}</div>
                      </div>
                    )}
                  </div>
                );
              })}
          </div>

          {/* Hour ruler: clock time and the Gospels' own hours */}
          {hourly && (
            <div
              style={{
                position: 'relative',
                height: '1.9rem',
                marginBottom: '0.4rem',
                borderBottom: `1px solid ${theme.border}`,
              }}
            >
              {hourTicks.map((h) => (
                <div
                  key={h}
                  style={{
                    position: 'absolute',
                    left: xOf(h),
                    top: 0,
                    bottom: 0,
                    borderLeft: `1px solid ${theme.border}`,
                    paddingLeft: '2px',
                  }}
                >
                  <div style={{ fontSize: '0.6rem', fontWeight: 700, whiteSpace: 'nowrap' }}>
                    {clock(h)}
                  </div>
                  <div
                    style={{ fontSize: '0.58rem', color: theme.textMuted, whiteSpace: 'nowrap' }}
                  >
                    {gospelHour(h)}
                  </div>
                </div>
              ))}
            </div>
          )}

          {showThree && (
            <div style={{ marginBottom: '0.6rem' }}>
              <div
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  color: '#0f766e',
                  marginBottom: '2px',
                }}
              >
                Three days and three nights (Matthew 12:40): three days touched, two nights
              </div>
              <div style={{ position: 'relative', height: '24px' }}>
                {P.three_days
                  .filter((b) => inRange(b.at, b.end))
                  .map((b) => (
                    <button
                      key={b.label}
                      onClick={() =>
                        setSelected({
                          kind: 'dated',
                          id: b.label,
                          label: b.label,
                          when: when(b.at, b.end),
                          refs: 'Matthew 12:40; 27:63-64; Luke 24:21',
                          note: `${b.note} ${P.three_days_note}`,
                          study_ref: 'jesus/three-days-and-three-nights',
                        })
                      }
                      title={`${b.label}: ${b.note}`}
                      style={{
                        position: 'absolute',
                        left: xOf(b.at),
                        width: Math.max(8, xOf(b.end) - xOf(b.at)),
                        top: 0,
                        height: 22,
                        borderRadius: '4px',
                        border: '1.5px solid #0f766e',
                        background:
                          b.kind === 'night'
                            ? 'rgba(15, 118, 110, 0.75)'
                            : 'rgba(15, 118, 110, 0.18)',
                        color: b.kind === 'night' ? 'white' : theme.text,
                        fontSize: '0.68rem',
                        overflow: 'hidden',
                        whiteSpace: 'nowrap',
                        cursor: 'pointer',
                      }}
                    >
                      {b.label}
                    </button>
                  ))}
              </div>
            </div>
          )}

          {tracks.map((t) => {
            const rows = stackRows(
              items.filter((e) => e.track === t.id).sort((a, b) => a.at - b.at),
              xOf,
              hourly ? 190 : 150
            );
            if (!rows.length) return null;
            const n = Math.max(1, ...rows.map((r) => r.row + 1));
            return (
              <div key={t.id} style={{ marginBottom: '0.6rem' }}>
                <div
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: t.color,
                    marginBottom: '2px',
                  }}
                >
                  {t.label}
                </div>
                <div style={{ position: 'relative', height: `${n * 28}px` }}>
                  {rows.map((e) => {
                    const c = CERTAINTY_META[e.certainty ?? 'stated'];
                    const isBar = e.end != null;
                    const left = xOf(e.at);
                    return (
                      <button
                        key={e.id}
                        onClick={() => choose(e)}
                        title={`${e.label} · ${when(e.at, e.end)}`}
                        style={{
                          position: 'absolute',
                          left: isBar ? left : left - 5,
                          width: isBar ? Math.max(8, xOf(e.end) - left) : 'auto',
                          minWidth: 10,
                          top: e.row * 28,
                          height: 22,
                          padding: '0 6px',
                          borderRadius: '4px',
                          border: `1.5px ${c.dashed || e.timing === 'approx' ? 'dashed' : 'solid'} ${t.color}`,
                          background: 'transparent',
                          boxShadow: `inset 0 0 0 999px ${t.color}${Math.round(c.opacity * 255)
                            .toString(16)
                            .padStart(2, '0')}`,
                          color: c.opacity > 0.6 ? 'white' : theme.text,
                          fontSize: '0.68rem',
                          textAlign: 'left',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          cursor: 'pointer',
                          outline: selected?.id === e.id ? `2px solid ${theme.primary}` : 'none',
                        }}
                      >
                        {e.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <DetailPanel
        selected={selected?.kind === 'dated' ? selected : null}
        theme={theme}
        activeEpochs={[]}
        markerDate={() => ''}
      />

      <div style={{ marginTop: '1.25rem' }}>
        <div
          style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            color: theme.textMuted,
            marginBottom: '0.4rem',
          }}
        >
          IN THIS VIEW ({items.length})
          {hourly ? ' · dashed borders: hour approximate, order as the text gives it' : ''}
        </div>
        <div style={{ border: `1px solid ${theme.border}`, borderRadius: '0.5rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
            <tbody>
              {[...items]
                .sort((a, b) => a.at - b.at)
                .map((e) => (
                  <tr
                    key={`row-${e.id}`}
                    onClick={() => choose(e)}
                    style={{ cursor: 'pointer', borderBottom: `1px solid ${theme.border}` }}
                  >
                    <td style={{ padding: '0.3rem 0.5rem', whiteSpace: 'nowrap', fontWeight: 600 }}>
                      {when(e.at, e.end)}
                    </td>
                    <td
                      style={{
                        padding: '0.3rem 0.5rem',
                        whiteSpace: 'nowrap',
                        color: theme.textMuted,
                      }}
                    >
                      {gospelHour(e.at)}
                    </td>
                    <td style={{ padding: '0.3rem 0.5rem' }}>{e.label}</td>
                    <td style={{ padding: '0.3rem 0.5rem', color: theme.textMuted }}>{e.refs}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
