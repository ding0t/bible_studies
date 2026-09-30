import React, { useEffect, useMemo, useState } from 'react';
import {
  CHRONOLOGY,
  GENEALOGY_INDEX,
  amToGregorian,
  gregorianToAm,
  loadEvents,
  loadGenealogyPeople,
  mergePeopleWithVariant,
} from '../../utils/chronology';
import {
  BASE_WIDTH,
  CORE_ONLY_SPAN,
  EPOCH_META,
  LAYER_META,
  LIFE_EVENTS_SPAN,
  PERIODS,
  VARIANT_META,
  chip,
  formatGregorian,
  markerDateFor,
  parseGregorian,
  sectionLabel,
  theme,
} from './shared';
import TimeChart from './TimeChart';
import PersonPanel from './PersonPanel';
import DetailPanel from './DetailPanel';
import FutureSequence from './FutureSequence';
import DatedSequence from './DatedSequence';
import FamilyTree from './FamilyTree';

// The view lives in the address bar so any view can be shared: #christ, #kingdom-exile&person=hezekiah,
// #view=family&person=abraham.
function readHash() {
  if (typeof window === 'undefined') return {};
  const out = {};
  for (const part of window.location.hash.replace(/^#/, '').split('&').filter(Boolean)) {
    const [k, v] = part.split('=');
    if (v === undefined) out.period = decodeURIComponent(k);
    else out[k] = decodeURIComponent(v);
  }
  if (out.period && !PERIODS.some((p) => p.id === out.period)) delete out.period;
  return out;
}

function writeHash({ period, person, view }) {
  if (typeof window === 'undefined') return;
  const parts = [];
  if (period && period !== 'week') parts.push(period);
  if (view && view !== 'chart') parts.push(`view=${view}`);
  if (person) parts.push(`person=${person}`);
  const hash = parts.length ? `#${parts.join('&')}` : ' ';
  window.history.replaceState(null, '', hash === ' ' ? window.location.pathname : hash);
}

export default function ChronologyExplorer({
  events = [],
  initialPeriod = null,
  initialView = null,
  initialPerson = null,
}) {
  const fromHash = useMemo(() => readHash(), []);
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
  const [periodId, setPeriodId] = useState(() => initialPeriod ?? fromHash.period ?? 'week');
  const [view, setView] = useState(() => initialView ?? fromHash.view ?? 'chart');
  const [personId, setPersonId] = useState(() => initialPerson ?? fromHash.person ?? null);
  const [custom, setCustom] = useState(null);
  const [fromText, setFromText] = useState('');
  const [toText, setToText] = useState('');
  const [rangeError, setRangeError] = useState('');
  const [zoom, setZoom] = useState(1);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState('');
  const [showEveryone, setShowEveryone] = useState(false);

  useEffect(
    () => writeHash({ period: custom ? null : periodId, person: personId, view }),
    [periodId, personId, view, custom]
  );

  const genealogyPeople = useMemo(() => loadGenealogyPeople(), []);
  const primaryEpoch = activeEpochs[0] ?? 'genealogy';
  const period = PERIODS.find((p) => p.id === periodId) ?? PERIODS[0];
  const isFuture = !custom && Boolean(period.future);
  const isDated = !custom && Boolean(period.dated);

  const [amStart, amEnd] = useMemo(() => {
    if (custom) return custom;
    if (period.am) return period.am;
    if (period.greg) return period.greg.map((g) => gregorianToAm(g, primaryEpoch));
    return [0, 7000];
  }, [custom, period, primaryEpoch]);
  const span = amEnd - amStart;
  const width = BASE_WIDTH * zoom;

  const toggleInList = (list, setList, id) =>
    setList(list.includes(id) ? list.filter((x) => x !== id) : [...list, id]);
  const toggleLayer = (id) => setLayers((l) => ({ ...l, [id]: !l[id] }));
  const choosePeriod = (id) => {
    setCustom(null);
    setRangeError('');
    setPeriodId(id);
    setSelected(null);
    setView('chart');
  };
  const showRange = (a, b) => {
    setCustom([a, b]);
    setSelected(null);
    setView('chart');
  };
  const applyCustom = () => {
    const a = parseGregorian(fromText);
    const b = parseGregorian(toText);
    if (a == null || b == null || a >= b) {
      setRangeError('Enter two years, earliest first, e.g. "1000 BC" and "AD 100".');
      return;
    }
    setRangeError('');
    showRange(gregorianToAm(a, primaryEpoch), gregorianToAm(b, primaryEpoch));
  };

  const lanes = useMemo(
    () =>
      activeVariants.map((variantId) => ({
        variantId,
        // == null: a person absent from a tradition (Cainan outside the LXX) has undefined years.
        people: mergePeopleWithVariant(genealogyPeople, variantId).filter(
          (p) => p.gregorian_year_born != null
        ),
      })),
    [activeVariants, genealogyPeople]
  );
  const allPeople = lanes[0]?.people ?? mergePeopleWithVariant(genealogyPeople, 'mt');
  const person = personId
    ? (allPeople.find((p) => p.id === personId) ?? genealogyPeople.find((p) => p.id === personId))
    : null;

  // Every dated marker in one shape, from the one event list.
  const markers = useMemo(() => {
    const out = [];
    for (const e of loadEvents()) {
      if (e.am == null) continue;
      const layer = {
        genesis: 'genesis',
        anchor: 'anchor',
        archaeology: 'archaeology',
        milestone: 'milestone',
        life: 'life',
      }[e.source];
      if (!layer) continue; // the AD 33 sequence has its own hour-level views
      const am =
        e.source === 'anchor' || e.source === 'archaeology'
          ? gregorianToAm(e.gregorian_year, primaryEpoch)
          : e.am;
      out.push({
        ...e,
        layer,
        am,
        amTo: e.am_end ?? am,
        scripture: e.refs,
        note: e.note ?? e.description,
      });
    }
    for (const e of events || []) {
      if (typeof e.zadok_year === 'number')
        out.push({
          ...e,
          id: e.slug,
          label: e.title,
          layer: 'event',
          am: e.zadok_year,
          amTo: e.zadok_year,
        });
    }
    return out;
  }, [primaryEpoch, events]);

  const visibleMarkers = useMemo(
    () =>
      markers
        .filter((m) => layers[m.layer])
        .filter((m) => m.layer !== 'anchor' || m.core || span <= CORE_ONLY_SPAN)
        .filter((m) => m.layer !== 'life' || span <= LIFE_EVENTS_SPAN)
        .filter((m) => m.amTo >= amStart && m.am <= amEnd)
        .sort((a, b) => a.am - b.am),
    [markers, layers, amStart, amEnd, span]
  );

  const markerDate = (m) => markerDateFor(m, primaryEpoch, amToGregorian);
  const selectPerson = (id) => {
    setPersonId(id);
    setSelected(null);
  };
  const focusLife = (p) => {
    const pad = Math.max(10, Math.round((p.zadok_year_died - p.zadok_year_born) * 0.15));
    showRange(p.zadok_year_born - pad, p.zadok_year_died + pad);
  };
  const selectEvent = (e) => {
    if (e.source === 'passion') {
      setPeriodId(e.detail ? 'crucifixion' : 'passion-week');
      setCustom(null);
      setView('chart');
      setSelected({ kind: 'dated', ...e });
      return;
    }
    const am = e.am ?? 0;
    setSelected({
      kind: 'marker',
      ...e,
      layer: e.source === 'passion' ? 'milestone' : e.source === 'genesis' ? 'genesis' : e.source,
      am,
      amTo: am,
      scripture: e.refs,
      note: e.note ?? e.description,
    });
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
  const card = {
    padding: '1rem 1.25rem',
    background: theme.cardBg,
    border: `1px solid ${theme.border}`,
    borderRadius: '0.75rem',
    marginBottom: '0.75rem',
  };

  return (
    <div
      style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        color: theme.text,
      }}
    >
      <div style={card}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
          <button style={chip(view === 'chart', '#0f766e')} onClick={() => setView('chart')}>
            Timeline
          </button>
          <button style={chip(view === 'family', '#0f766e')} onClick={() => setView('family')}>
            Family tree
          </button>
        </div>
        {view === 'chart' && (
          <>
            <div style={sectionLabel}>PERIOD</div>
            <div
              style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}
            >
              {PERIODS.map((p) => (
                <button
                  key={p.id}
                  style={chip(
                    !custom && periodId === p.id,
                    p.future ? '#b45309' : p.dated ? '#be185d' : '#2563eb'
                  )}
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
              {rangeError && (
                <span style={{ fontSize: '0.8rem', color: '#b91c1c' }}>{rangeError}</span>
              )}
            </div>
          </>
        )}
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 600px', minWidth: 0 }}>
          {view === 'family' ? (
            <FamilyTree
              people={allPeople}
              selectedPersonId={personId}
              onSelectPerson={selectPerson}
            />
          ) : isDated ? (
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
              <div style={{ ...card, display: 'flex', flexWrap: 'wrap', gap: '1.25rem' }}>
                <div>
                  <div style={sectionLabel}>PEOPLE</div>
                  <div
                    style={{
                      display: 'flex',
                      gap: '0.5rem',
                      flexWrap: 'wrap',
                      alignItems: 'center',
                    }}
                  >
                    <input
                      style={{ ...input, width: '10rem' }}
                      placeholder="Find a person"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      aria-label="Find a person"
                    />
                    <button
                      style={chip(layers.genealogy, '#2563eb')}
                      onClick={() => toggleLayer('genealogy')}
                    >
                      Lifespans
                    </button>
                    {layers.genealogy && span > 2000 && (
                      <button
                        style={chip(showEveryone, '#2563eb')}
                        onClick={() => setShowEveryone((v) => !v)}
                      >
                        {showEveryone ? 'Everyone' : 'Key people only'}
                      </button>
                    )}
                  </div>
                </div>
                <div>
                  <div style={sectionLabel}>MARKERS</div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
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
                <div>
                  <div style={sectionLabel}>COMPARE</div>
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
                <div
                  style={{
                    marginLeft: 'auto',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
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
                      minWidth: '3rem',
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

              <div style={{ fontSize: '0.8rem', fontWeight: 700, margin: '0 0 0.4rem 0.2rem' }}>
                {formatGregorian(amToGregorian(Math.round(amStart), primaryEpoch))} –{' '}
                {formatGregorian(amToGregorian(Math.round(amEnd), primaryEpoch))} · AM{' '}
                {Math.round(amStart)}–{Math.round(amEnd)}
              </div>
              <TimeChart
                amStart={amStart}
                amEnd={amEnd}
                width={width}
                primaryEpoch={primaryEpoch}
                activeEpochs={activeEpochs}
                layers={layers}
                markers={visibleMarkers}
                lanes={lanes}
                showEveryone={showEveryone}
                search={search}
                selectedPersonId={personId}
                onSelectPerson={selectPerson}
                onSelectMarker={(m) => setSelected({ kind: 'marker', ...m })}
              />
              <DetailPanel
                selected={selected?.kind === 'marker' ? selected : null}
                theme={theme}
                activeEpochs={activeEpochs}
                markerDate={markerDate}
              />

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
                            style={{
                              padding: '0.3rem 0.5rem',
                              whiteSpace: 'nowrap',
                              fontWeight: 600,
                            }}
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
                            <span style={{ color: LAYER_META[m.layer].color, fontWeight: 700 }}>
                              ●
                            </span>{' '}
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
            </>
          )}
        </div>

        {person && (
          <PersonPanel
            person={person}
            people={allPeople}
            onSelectPerson={selectPerson}
            onSelectEvent={selectEvent}
            onFocusLife={focusLife}
            onClose={() => setPersonId(null)}
          />
        )}
      </div>

      <p style={{ fontSize: '0.8rem', color: theme.textMuted, marginTop: '1rem' }}>
        Anno Mundi (years since creation) on this site's chronology: the Masoretic numbers, creation
        3959 BC — the "a day is a thousand years" frame (2 Peter 3:8). Pick a period or type a range
        to zoom, or a person to follow their life; filled anchor markers are Fixed, hollow ones
        Anchored or Bracketed, and whiskers show the error bar. Turn on the Septuagint, the
        Samaritan Pentateuch or the dsscalendar.org epoch to compare.
      </p>
    </div>
  );
}
