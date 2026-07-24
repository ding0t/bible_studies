import React, { useState, useMemo } from 'react';
import {
  CHRONOLOGY,
  amToGregorian,
  gregorianToAm,
  mergePeopleWithVariant,
  loadGenealogyPeople,
  GENEALOGY_INDEX,
} from '../utils/chronology';

const AM_MIN = 0;
const AM_MAX = 7000;
const BASE_WIDTH = 1600;
const ROW_HEIGHT = 26;

const VARIANT_META = {
  mt: { label: 'Masoretic Text', color: '#2563eb' },
  lxx: { label: 'Septuagint', color: '#7c3aed' },
  sp: { label: 'Samaritan Pentateuch', color: '#059669' },
  harmonized_v1: { label: 'Proposed synthesis', color: '#d97706' },
};

const EPOCH_META = {
  genealogy: { color: '#475569' },
  millennial_2075: { color: '#e11d48' },
};

function formatGregorian(year) {
  if (year === null || year === undefined) return 'unknown';
  return year < 0 ? `${Math.abs(year)} BC` : `${year} AD`;
}

function studyUrl(studyRef) {
  return `/${studyRef}/`;
}

export default function MillennialWeek({ events = [] }) {
  const [activeVariants, setActiveVariants] = useState(['mt', 'harmonized_v1']);
  const [activeEpochs, setActiveEpochs] = useState(['genealogy', 'millennial_2075']);
  const [showAnchors, setShowAnchors] = useState(true);
  const [showMilestones, setShowMilestones] = useState(true);
  const [showGenealogy, setShowGenealogy] = useState(true);
  const [showEvents, setShowEvents] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [selected, setSelected] = useState(null);

  const genealogyPeople = useMemo(() => loadGenealogyPeople(), []);
  const lineages = GENEALOGY_INDEX.lineages;

  const width = BASE_WIDTH * zoom;
  const amToX = (am) => ((am - AM_MIN) / (AM_MAX - AM_MIN)) * width;

  const toggleInList = (list, setList, id) => {
    setList(list.includes(id) ? list.filter((x) => x !== id) : [...list, id]);
  };

  const primaryEpoch = activeEpochs[0] ?? 'genealogy';

  // Variant lanes: one per active variant, each a full patriarch list with
  // Adam-Terah overridden by that variant's tradition.
  const variantLanes = useMemo(
    () =>
      activeVariants.map((variantId) => ({
        variantId,
        people: mergePeopleWithVariant(genealogyPeople, variantId).filter(
          (p) => p.gregorian_year_born !== null && p.gregorian_year_died !== null
        ),
      })),
    [activeVariants, genealogyPeople]
  );

  // Anchors/milestones placed on the AM axis via the primary active epoch
  // (external history is dated in Gregorian years; AM is a projection of that).
  const placedAnchors = useMemo(
    () =>
      CHRONOLOGY.anchors.map((a) => ({
        ...a,
        am: gregorianToAm(a.gregorian_year, primaryEpoch),
      })),
    [primaryEpoch]
  );

  const placedMilestones = useMemo(
    () =>
      CHRONOLOGY.milestones.map((m) => ({
        ...m,
        am: m.am_year ?? gregorianToAm(m.gregorian_year, primaryEpoch),
      })),
    [primaryEpoch]
  );

  const placedEvents = useMemo(
    () =>
      (events || [])
        .filter((e) => typeof e.zadok_year === 'number')
        .map((e) => ({ ...e, am: e.zadok_year })),
    [events]
  );

  // Tick marks every 500 AM years, with each active epoch's Gregorian reading below.
  const ticks = useMemo(() => {
    const out = [];
    for (let am = AM_MIN; am <= AM_MAX; am += 500) out.push(am);
    return out;
  }, []);

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

  return (
    <div style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', color: theme.text }}>
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
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: theme.textMuted, marginBottom: '0.4rem' }}>
            CHRONOLOGY PATHS
          </div>
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
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: theme.textMuted, marginBottom: '0.4rem' }}>
            CREATION EPOCH
          </div>
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
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: theme.textMuted, marginBottom: '0.4rem' }}>
            LAYERS
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button style={chip(showGenealogy, '#2563eb')} onClick={() => setShowGenealogy((v) => !v)}>
              Genealogy
            </button>
            <button style={chip(showAnchors, '#0891b2')} onClick={() => setShowAnchors((v) => !v)}>
              Archaeology
            </button>
            <button style={chip(showMilestones, '#be185d')} onClick={() => setShowMilestones((v) => !v)}>
              Prophecy
            </button>
            <button style={chip(showEvents, '#65a30d')} onClick={() => setShowEvents((v) => !v)}>
              Studies
            </button>
          </div>
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button style={chip(false, theme.textMuted)} onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}>
            − Zoom
          </button>
          <span style={{ fontSize: '0.8rem', color: theme.textMuted, minWidth: '3.5rem', textAlign: 'center' }}>
            {Math.round(zoom * 100)}%
          </span>
          <button style={chip(false, theme.textMuted)} onClick={() => setZoom((z) => Math.min(3, z + 0.25))}>
            + Zoom
          </button>
        </div>
      </div>

      {/* The week */}
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
          {/* Day bands */}
          <div style={{ position: 'relative', height: '2rem', marginBottom: '0.25rem' }}>
            {CHRONOLOGY.millennial_days.map((d) => (
              <div
                key={d.day}
                title={d.label ?? `Day ${d.day}`}
                style={{
                  position: 'absolute',
                  left: amToX(d.am_start),
                  width: amToX(d.am_end) - amToX(d.am_start),
                  top: 0,
                  bottom: 0,
                  background: d.is_millennial_reign ? 'rgba(217, 119, 6, 0.22)' : d.day % 2 ? 'rgba(100,116,139,0.08)' : 'rgba(100,116,139,0.03)',
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

          {/* AM ruler + per-epoch Gregorian readouts */}
          <div style={{ position: 'relative', height: `${16 + activeEpochs.length * 14}px`, borderBottom: `2px solid ${theme.borderStrong}`, marginBottom: '0.5rem' }}>
            {ticks.map((am) => (
              <div key={am} style={{ position: 'absolute', left: amToX(am), top: 0, bottom: 0, borderLeft: `1px solid ${theme.border}`, textAlign: 'left' }}>
                <div style={{ fontSize: '0.65rem', fontWeight: 700, color: theme.textMuted, marginLeft: '2px' }}>AM {am}</div>
                {activeEpochs.map((epochId) => (
                  <div key={epochId} style={{ fontSize: '0.6rem', color: EPOCH_META[epochId].color, marginLeft: '2px' }}>
                    {formatGregorian(amToGregorian(am, epochId))}
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Anchors + milestones + events markers */}
          <div style={{ position: 'relative', height: '2.25rem', marginBottom: '0.5rem' }}>
            {showAnchors &&
              placedAnchors.map(
                (a) =>
                  a.am !== null && (
                    <button
                      key={a.id}
                      onClick={() => setSelected({ kind: 'anchor', ...a })}
                      title={a.label}
                      style={{
                        position: 'absolute',
                        left: amToX(a.am) - 4,
                        top: 0,
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: '#0891b2',
                        border: '1.5px solid white',
                        cursor: 'pointer',
                        padding: 0,
                      }}
                    />
                  )
              )}
            {showMilestones &&
              placedMilestones.map(
                (m) =>
                  m.am !== null && (
                    <button
                      key={m.id}
                      onClick={() => setSelected({ kind: 'milestone', ...m })}
                      title={m.label}
                      style={{
                        position: 'absolute',
                        left: amToX(m.am) - 4,
                        top: 14,
                        width: 0,
                        height: 0,
                        borderLeft: '5px solid transparent',
                        borderRight: '5px solid transparent',
                        borderBottom: '8px solid #be185d',
                        cursor: 'pointer',
                        padding: 0,
                        background: 'none',
                        border: 'none',
                        borderBottomColor: '#be185d',
                      }}
                    />
                  )
              )}
            {showEvents &&
              placedEvents.map((e) => (
                <button
                  key={e.slug}
                  onClick={() => setSelected({ kind: 'event', ...e })}
                  title={e.title}
                  style={{
                    position: 'absolute',
                    left: amToX(e.am) - 3,
                    top: 26,
                    width: 6,
                    height: 6,
                    borderRadius: '1px',
                    background: '#65a30d',
                    border: '1px solid white',
                    cursor: 'pointer',
                    padding: 0,
                  }}
                />
              ))}
          </div>

          {/* Genealogy lanes, one per active variant */}
          {showGenealogy &&
            variantLanes.map(({ variantId, people }) => (
              <div key={variantId} style={{ marginBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: VARIANT_META[variantId].color, marginBottom: '2px' }}>
                  {VARIANT_META[variantId].label}
                </div>
                <div style={{ position: 'relative', height: `${ROW_HEIGHT}px` }}>
                  {people.map((p) => {
                    const amBorn = p.zadok_year_born;
                    const amDied = p.zadok_year_died;
                    const lineageColor = p.lineages?.includes('jesus_line')
                      ? lineages.jesus_line.color
                      : lineages.seth_line?.color ?? VARIANT_META[variantId].color;
                    return (
                      <div
                        key={p.id}
                        onClick={() => setSelected({ kind: 'person', variantId, ...p })}
                        title={`${p.name}: ${formatGregorian(amToGregorian(amBorn, primaryEpoch))} – ${formatGregorian(amToGregorian(amDied, primaryEpoch))} (${p.lifespan_years}y)`}
                        style={{
                          position: 'absolute',
                          left: amToX(amBorn),
                          width: Math.max(2, amToX(amDied) - amToX(amBorn)),
                          top: 4,
                          height: ROW_HEIGHT - 8,
                          background: lineageColor,
                          opacity: 0.75,
                          borderRadius: '2px',
                          cursor: 'pointer',
                        }}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Detail panel */}
      {selected && (
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
                {VARIANT_META[selected.variantId].label} · AM {selected.zadok_year_born}–{selected.zadok_year_died} ·{' '}
                {activeEpochs
                  .map((e) => `${formatGregorian(amToGregorian(selected.zadok_year_born, e))} (${e})`)
                  .join(' / ')}{' '}
                · {selected.lifespan_years} years
              </div>
              {selected.title && <p style={{ margin: 0 }}>{selected.title}</p>}
            </>
          )}
          {(selected.kind === 'anchor' || selected.kind === 'milestone') && (
            <>
              <h3 style={{ margin: '0 0 0.25rem 0' }}>{selected.label}</h3>
              <div style={{ fontSize: '0.85rem', color: theme.textMuted, marginBottom: '0.5rem' }}>
                AM {selected.am} ·{' '}
                {activeEpochs.map((e) => `${formatGregorian(amToGregorian(selected.am, e))} (${e})`).join(' / ')}
              </div>
              <p style={{ margin: 0 }}>{selected.evidence ?? selected.note}</p>
              {selected.study_ref && (
                <a href={studyUrl(selected.study_ref)} style={{ color: theme.primary, fontSize: '0.85rem' }}>
                  Read the study →
                </a>
              )}
            </>
          )}
          {selected.kind === 'event' && (
            <>
              <h3 style={{ margin: '0 0 0.25rem 0' }}>{selected.title}</h3>
              <div style={{ fontSize: '0.85rem', color: theme.textMuted, marginBottom: '0.5rem' }}>
                AM {selected.am} · {formatGregorian(selected.gregorian_year)}
              </div>
              <p style={{ margin: 0 }}>{selected.description}</p>
              {selected.url && (
                <a href={selected.url} style={{ color: theme.primary, fontSize: '0.85rem' }}>
                  Read the study →
                </a>
              )}
            </>
          )}
        </div>
      )}

      <p style={{ fontSize: '0.8rem', color: theme.textMuted, marginTop: '1rem' }}>
        Axis is Anno Mundi (years since creation, AM 0–7000) — the "a day is a thousand years" frame
        (2 Peter 3:8). Toggle chronology paths and creation epochs to see where the Flood, the Exodus,
        Christ, and Year 6000 land under each.
      </p>
    </div>
  );
}
