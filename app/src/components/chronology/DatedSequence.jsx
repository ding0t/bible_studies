import React from 'react';
import { CHRONOLOGY } from '../../utils/chronology';
import { CERTAINTY_META, stackRows, studyUrl } from './shared';
import DetailPanel from './DetailPanel';

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

export default function DatedSequence({ period, theme, width, selected, setSelected }) {
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
