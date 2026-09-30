import React from 'react';
import { CHRONOLOGY } from '../../utils/chronology';
import { CERTAINTY_META, stackRows } from './shared';
import DetailPanel from './DetailPanel';

// The future on its own axis: years of 360 days from the covenant of Daniel 9:27. No Gregorian or
// Anno Mundi year appears here, because Scripture gives these spans without their start.
export default function FutureSequence({ period, theme, width, selected, setSelected }) {
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
