import React, { useMemo, useRef, useState } from 'react';
import {
  CHRONOLOGY,
  GENEALOGY_INDEX,
  amToGregorian,
  gregorianToAm,
  eventsForPerson,
} from '../../utils/chronology';
import {
  CLASSIFICATION,
  CORE_ONLY_SPAN,
  EPOCH_META,
  LAYER_META,
  MARKER_ROW,
  SOURCE_LAYER,
  VARIANT_META,
  formatGregorian,
  markerDateFor,
  niceStep,
  sectionLabel,
  theme,
} from './shared';

const LABEL_W = 150;
const GANTT_ROW = 20;
// Wider than this and the Gantt shows the key people only, unless the reader asks for everyone.
const KEY_PEOPLE_SPAN = 2000;

const hatch = (color) => `repeating-linear-gradient(135deg, ${color} 0 4px, ${color}55 4px 8px)`;

// The Anno Mundi chart: day bands, a ruler in AM and Gregorian years, one row of markers per layer,
// then the Gantt -- a row per person, with the events they are tagged in marked on their row. Hover
// anywhere for the people alive that year; click to pin it.
export default function TimeChart({
  amStart,
  amEnd,
  width,
  primaryEpoch,
  activeEpochs,
  layers,
  markers,
  lanes,
  showEveryone,
  search,
  selectedPersonId,
  onSelectPerson,
  onSelectMarker,
}) {
  const span = amEnd - amStart;
  const amToX = (am) => ((am - amStart) / span) * width;
  const clipX = (am) => amToX(Math.min(Math.max(am, amStart), amEnd));
  const inView = (am, amTo = am) => amTo >= amStart && am <= amEnd;
  const toGreg = (am) => amToGregorian(Math.round(am), primaryEpoch);
  const markerDate = (m) => markerDateFor(m, primaryEpoch, amToGregorian);
  const innerRef = useRef(null);
  const [hoverAm, setHoverAm] = useState(null);
  const [pinnedAm, setPinnedAm] = useState(null);

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

  const [primary, ...others] = lanes;
  const q = search.trim().toLowerCase();
  const ganttPeople = useMemo(() => {
    if (!primary) return [];
    return primary.people
      .filter((p) => p.zadok_year_born != null && p.zadok_year_died != null)
      .filter((p) => inView(p.zadok_year_born, p.zadok_year_died))
      .filter(
        (p) =>
          !q ||
          p.name.toLowerCase().includes(q) ||
          p.name_transliteration?.toLowerCase().includes(q) ||
          p.name_hebrew?.includes(search.trim())
      )
      .filter(
        (p) =>
          q ||
          showEveryone ||
          span <= KEY_PEOPLE_SPAN ||
          p.significance_level === 1 ||
          p.id === selectedPersonId
      )
      .sort((a, b) => a.zadok_year_born - b.zadok_year_born);
  }, [primary, amStart, amEnd, q, showEveryone, selectedPersonId]);
  const otherById = others.map((l) => ({
    variantId: l.variantId,
    byId: new Map(l.people.map((p) => [p.id, p])),
  }));

  const eras = Object.values(GENEALOGY_INDEX.eras);
  const eraOf = (am) =>
    eras.find((e) => am >= e.am_start && am < e.am_end)?.name ?? 'After the Second Temple';

  const alive = (am) =>
    am == null
      ? []
      : (primary?.people ?? []).filter(
          (p) =>
            p.zadok_year_born != null &&
            p.zadok_year_died != null &&
            p.zadok_year_born <= am &&
            am <= p.zadok_year_died
        );

  const onMove = (e) => {
    const rect = innerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left - LABEL_W;
    if (x < 0 || x > width) return setHoverAm(null);
    setHoverAm(amStart + (x / width) * span);
  };

  const lineageColor = (p) =>
    p.lineages?.includes('jesus_line')
      ? GENEALOGY_INDEX.lineages.jesus_line.color
      : GENEALOGY_INDEX.lineages.seth_line.color;
  const markerRows = ['genesis', 'anchor', 'archaeology', 'milestone', 'life', 'event'].filter(
    (l) => layers[l] && markers.some((m) => m.layer === l)
  );

  let lastEra = null;
  const cursorAm = hoverAm ?? pinnedAm;

  return (
    <div
      style={{
        overflowX: 'auto',
        background: theme.bgElevated,
        border: `1px solid ${theme.border}`,
        borderRadius: '0.75rem',
        padding: '1rem 1rem 1rem 0',
      }}
    >
      <div
        ref={innerRef}
        onMouseMove={onMove}
        onMouseLeave={() => setHoverAm(null)}
        onClick={(e) => {
          if (e.target === e.currentTarget || e.target.dataset?.chartBg) setPinnedAm(hoverAm);
        }}
        style={{ position: 'relative', width: `${LABEL_W + width}px` }}
      >
        {/* Day bands */}
        <Row label="" height="1.6rem">
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
        </Row>

        {/* Ruler */}
        <Row
          label=""
          height={`${18 + activeEpochs.length * 14}px`}
          style={{ borderBottom: `2px solid ${theme.borderStrong}`, marginBottom: '0.4rem' }}
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
                paddingLeft: '2px',
              }}
            >
              <div
                style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  color: theme.textMuted,
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
                    whiteSpace: 'nowrap',
                  }}
                >
                  {formatGregorian(amToGregorian(Math.round(am), epochId))}
                </div>
              ))}
            </div>
          ))}
        </Row>

        {/* Marker rows */}
        {markerRows.map((layer) => (
          <Row
            key={layer}
            label={LAYER_META[layer].label}
            labelColor={LAYER_META[layer].color}
            height={`${MARKER_ROW}px`}
          >
            {markers
              .filter((m) => m.layer === layer)
              .map((m) => {
                const color = LAYER_META[layer].color;
                const isRange = m.amTo !== m.am;
                const pm = Number((m.error ?? '').replace('±', ''));
                const errPx = Number.isFinite(pm) && pm > 0 ? amToX(m.am + pm) - amToX(m.am) : 0;
                return (
                  <button
                    key={`${layer}-${m.id}`}
                    onClick={() => onSelectMarker(m)}
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
                        m.tier === 'Anchored' || m.tier === 'Bracketed' ? 'transparent' : color,
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
          </Row>
        ))}

        {/* The Gantt: one row per person */}
        {layers.genealogy &&
          ganttPeople.map((p) => {
            const era = eraOf(p.zadok_year_born);
            const header = era !== lastEra;
            lastEra = era;
            const cls = CLASSIFICATION[p.data_classification];
            const color = lineageColor(p);
            const left = clipX(p.zadok_year_born);
            const w = Math.max(3, clipX(p.zadok_year_died) - left);
            const selected = p.id === selectedPersonId;
            const ticksOnRow = eventsForPerson(p.id).filter(
              (e) => e.am != null && inView(e.am) && layers[SOURCE_LAYER[e.source]] !== false
            );
            return (
              <React.Fragment key={p.id}>
                {header && (
                  <div
                    style={{
                      position: 'sticky',
                      left: 0,
                      width: LABEL_W + 200,
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      color: theme.textMuted,
                      padding: '0.5rem 0 0.15rem 0.6rem',
                    }}
                  >
                    {era}
                  </div>
                )}
                <Row
                  label={p.name}
                  labelColor={selected ? theme.primary : theme.text}
                  onLabel={() => onSelectPerson(p.id)}
                  height={`${GANTT_ROW}px`}
                  style={{ background: selected ? theme.selectedBg : 'transparent' }}
                >
                  {otherById.map(({ variantId, byId }) => {
                    const o = byId.get(p.id);
                    if (
                      !o ||
                      o.zadok_year_born == null ||
                      (o.zadok_year_born === p.zadok_year_born &&
                        o.zadok_year_died === p.zadok_year_died)
                    )
                      return null;
                    const ol = clipX(o.zadok_year_born);
                    return (
                      <div
                        key={variantId}
                        title={`${p.name} in the ${VARIANT_META[variantId].label}: AM ${o.zadok_year_born}–${o.zadok_year_died}`}
                        style={{
                          position: 'absolute',
                          left: ol,
                          width: Math.max(3, clipX(o.zadok_year_died) - ol),
                          top: 3,
                          height: GANTT_ROW - 6,
                          border: `1.5px dashed ${VARIANT_META[variantId].color}`,
                          borderRadius: '3px',
                          pointerEvents: 'none',
                        }}
                      />
                    );
                  })}
                  <button
                    onClick={() => onSelectPerson(p.id)}
                    title={`${p.name}: ${formatGregorian(p.gregorian_year_born)} – ${formatGregorian(p.gregorian_year_died)} (${p.lifespan_years} years)${cls ? ` · ${cls.label}` : ''}`}
                    style={{
                      position: 'absolute',
                      left,
                      width: w,
                      top: 4,
                      height: GANTT_ROW - 8,
                      padding: 0,
                      border: selected ? `2px solid ${theme.text}` : 'none',
                      borderRadius: '3px',
                      background: cls?.hatched ? hatch(color) : color,
                      opacity: 0.8,
                      cursor: 'pointer',
                    }}
                  />
                  {ticksOnRow.map((e) => (
                    <button
                      key={`${e.source}-${e.id}`}
                      onClick={() =>
                        onSelectMarker({
                          ...e,
                          layer: SOURCE_LAYER[e.source],
                          am: e.am,
                          amTo: e.am,
                          gregorian_year:
                            e.source === 'anchor' || e.source === 'archaeology'
                              ? e.gregorian_year
                              : undefined,
                        })
                      }
                      title={`${e.label} · ${formatGregorian(e.gregorian)}`}
                      style={{
                        position: 'absolute',
                        left: amToX(e.am) - 1.5,
                        top: 1,
                        width: 3,
                        height: GANTT_ROW - 2,
                        padding: 0,
                        border: 'none',
                        background: LAYER_META[SOURCE_LAYER[e.source]].color,
                        cursor: 'pointer',
                      }}
                    />
                  ))}
                </Row>
              </React.Fragment>
            );
          })}

        {/* Year cursor */}
        {cursorAm != null && (
          <>
            <div
              data-chart-bg="1"
              style={{
                position: 'absolute',
                left: LABEL_W + amToX(cursorAm),
                top: 0,
                bottom: 0,
                width: 0,
                borderLeft: `1px ${pinnedAm != null && hoverAm == null ? 'solid' : 'dashed'} ${theme.primary}`,
                pointerEvents: 'none',
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: LABEL_W + amToX(cursorAm) + 4,
                top: 0,
                fontSize: '0.68rem',
                background: theme.bgElevated,
                border: `1px solid ${theme.border}`,
                borderRadius: '4px',
                padding: '0 4px',
                pointerEvents: 'none',
                whiteSpace: 'nowrap',
              }}
            >
              {formatGregorian(toGreg(cursorAm))} · AM {Math.round(cursorAm)} ·{' '}
              {alive(Math.round(cursorAm)).length} alive
            </div>
          </>
        )}
      </div>

      {layers.genealogy && ganttPeople.length === 0 && (
        <div style={{ paddingLeft: '1rem', fontSize: '0.8rem', color: theme.textMuted }}>
          No one in the genealogy lived in this range.
        </div>
      )}

      {pinnedAm != null && (
        <div style={{ margin: '0.75rem 0 0 1rem', fontSize: '0.82rem' }}>
          <div style={sectionLabel}>
            ALIVE IN {formatGregorian(toGreg(pinnedAm)).toUpperCase()} (AM {Math.round(pinnedAm)}){' '}
            <button
              onClick={() => setPinnedAm(null)}
              style={{
                background: 'none',
                border: 'none',
                color: theme.primary,
                cursor: 'pointer',
              }}
            >
              clear
            </button>
          </div>
          {alive(Math.round(pinnedAm)).map((p, i) => (
            <span key={p.id}>
              {i > 0 && ' · '}
              <button
                onClick={() => onSelectPerson(p.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  color: theme.primary,
                  cursor: 'pointer',
                  font: 'inherit',
                }}
              >
                {p.name}
              </button>{' '}
              <span style={{ color: theme.textMuted }}>
                ({Math.round(pinnedAm) - p.zadok_year_born})
              </span>
            </span>
          ))}
        </div>
      )}
      <div style={{ margin: '0.6rem 0 0 1rem', fontSize: '0.72rem', color: theme.textMuted }}>
        Hover for the year; click the chart to list who was alive then. Hatched bars are estimated
        or calculated; dashed outlines are the same life in another manuscript tradition. Ticks on a
        row are that person's events.
        {span > CORE_ONLY_SPAN ? ' Pick a period to see every anchor.' : ''}
      </div>
    </div>
  );
}

// One chart row: a sticky name cell, then the track the children are positioned in.
function Row({ label, labelColor, onLabel, height, style, children }) {
  return (
    <div style={{ position: 'relative', display: 'flex', height, ...style }}>
      <div
        onClick={onLabel}
        style={{
          position: 'sticky',
          left: 0,
          zIndex: 2,
          width: LABEL_W,
          flex: `0 0 ${LABEL_W}px`,
          background: theme.bgElevated,
          fontSize: '0.72rem',
          color: labelColor ?? theme.textMuted,
          padding: '0 0.4rem 0 0.9rem',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          lineHeight: height,
          cursor: onLabel ? 'pointer' : 'default',
        }}
      >
        {label}
      </div>
      <div data-chart-bg="1" style={{ position: 'relative', flex: '1 1 auto' }}>
        {children}
      </div>
    </div>
  );
}
