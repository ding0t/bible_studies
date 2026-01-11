import React, { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, ChevronLeft, ChevronRight } from 'lucide-react';

export default function TimelineComponent({ events = [] }) {
  const [zoom, setZoom] = useState(1);
  const [selected, setSelected] = useState(null);
  const [scroll, setScroll] = useState(0);
  const [calendarView, setCalendarView] = useState('gregorian'); // 'gregorian' or 'essene'

  useEffect(() => {
    if (events.length > 0) {
      const sorted = [...events].sort((a, b) => {
        const aYear = calendarView === 'essene' ? (a.essene_year || a.year) : (a.gregorian_year || a.year);
        const bYear = calendarView === 'essene' ? (b.essene_year || b.year) : (b.gregorian_year || b.year);
        return aYear - bYear;
      });
      setSelected(sorted[0]);
    }
  }, [events, calendarView]);

  const handleZoomIn = () => setZoom(z => Math.min(z * 1.3, 3));
  const handleZoomOut = () => setZoom(z => Math.max(z / 1.3, 0.5));
  const handleScroll = (direction) => {
    setScroll(s => s + (direction === 'left' ? -100 : 100));
  };

  const displayYears = events.map(e => {
    if (calendarView === 'essene') {
      return e.essene_year || e.year || 0;
    } else {
      return e.gregorian_year || e.year || 0;
    }
  });

  const yearRange = displayYears.length > 0 ? {
    min: Math.min(...displayYears) - 100,
    max: Math.max(...displayYears) + 100
  } : { min: 1900, max: 2030 };
  
  const rangeSpan = yearRange.max - yearRange.min;

  return (
    <div className="timeline-container">
      <style>{`
        .timeline-container {
          width: 100%;
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .timeline-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .controls {
          display: flex;
          gap: 0.5rem;
        }
        button {
          padding: 0.5rem 1rem;
          border: 1px solid #3b82f6;
          background: #dbeafe;
          color: #1e40af;
          border-radius: 0.5rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          transition: all 0.2s;
        }
        button:hover {
          background: #bfdbfe;
          border-color: #1e40af;
        }
        .zoom-level {
          font-size: 0.875rem;
          color: #666;
          min-width: 60px;
          text-align: center;
        }
        .timeline-wrapper {
          position: relative;
          overflow-x: auto;
          background: #f8fafc;
          border-radius: 0.75rem;
          padding: 2rem;
          margin-bottom: 2rem;
        }
        .timeline-track {
          display: flex;
          gap: ${40 * (rangeSpan / 500)}px;
          min-width: ${(rangeSpan / 500) * 40 * zoom}px;
          transform: translateX(${scroll}px);
          transition: transform 0.3s ease;
          position: relative;
          padding: 1rem 0;
        }
        .timeline-track::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 2px;
          background: #cbd5e1;
          transform: translateY(-50%);
        }
        .timeline-event {
          position: relative;
          flex-shrink: 0;
          width: ${40 * zoom}px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .timeline-dot {
          width: ${8 * zoom}px;
          height: ${8 * zoom}px;
          background: #64748b;
          border: 2px solid white;
          border-radius: 50%;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          z-index: 10;
          transition: all 0.2s;
        }
        .timeline-event.active .timeline-dot {
          width: ${16 * zoom}px;
          height: ${16 * zoom}px;
          background: #3b82f6;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
        }
        .timeline-event:hover .timeline-dot {
          background: #1e40af;
          box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.2);
        }
        .timeline-label {
          position: absolute;
          top: 100%;
          left: 50%;
          transform: translateX(-50%);
          margin-top: 1rem;
          font-size: ${0.75 * zoom}rem;
          font-weight: 600;
          color: #334155;
          white-space: nowrap;
          pointer-events: none;
        }
        .timeline-event.active .timeline-label {
          color: #3b82f6;
          font-weight: 700;
        }
        .details {
          background: white;
          border: 2px solid #e2e8f0;
          border-radius: 0.75rem;
          padding: 1.5rem;
          margin-bottom: 1rem;
        }
        .details h2 {
          margin: 0 0 0.5rem 0;
          color: #1e293b;
          font-size: 1.5rem;
        }
        .details .year {
          color: #3b82f6;
          font-weight: 600;
          font-size: 0.875rem;
          margin-bottom: 0.5rem;
        }
        .details p {
          margin: 0;
          color: #475569;
          line-height: 1.6;
        }
        .scroll-hints {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: #94a3b8;
          margin-top: 1rem;
        }
        .empty-state {
          padding: 2rem;
          color: #666;
          text-align: center;
          background: #f8fafc;
          border-radius: 0.75rem;
        }
      `}</style>

      <div className="timeline-header">
        <h1 style={{ margin: 0, fontSize: '1.875rem', color: '#1e293b' }}>Prophetic Timeline</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '0.5rem', backgroundColor: '#e2e8f0', borderRadius: '0.5rem', padding: '0.25rem' }}>
            <button 
              onClick={() => setCalendarView('gregorian')}
              style={{
                padding: '0.5rem 1rem',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                backgroundColor: calendarView === 'gregorian' ? '#3b82f6' : 'transparent',
                color: calendarView === 'gregorian' ? 'white' : '#475569',
                fontWeight: calendarView === 'gregorian' ? '600' : '500',
                fontSize: '0.875rem',
                transition: 'all 0.2s'
              }}
            >
              Gregorian
            </button>
            <button 
              onClick={() => setCalendarView('essene')}
              style={{
                padding: '0.5rem 1rem',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                backgroundColor: calendarView === 'essene' ? '#3b82f6' : 'transparent',
                color: calendarView === 'essene' ? 'white' : '#475569',
                fontWeight: calendarView === 'essene' ? '600' : '500',
                fontSize: '0.875rem',
                transition: 'all 0.2s'
              }}
            >
              Essene
            </button>
          </div>
          <div className="controls">
            <button onClick={handleZoomOut}><ZoomOut size={18} />Zoom Out</button>
            <div className="zoom-level">{Math.round(zoom * 100)}%</div>
            <button onClick={handleZoomIn}><ZoomIn size={18} />Zoom In</button>
          </div>
        </div>
      </div>

      {events.length === 0 ? (
        <div className="empty-state">📋 No timeline events loaded. Add studies with a year field in frontmatter.</div>
      ) : (
        <div className="timeline-wrapper">
          <div className="timeline-track">
            {events.map(event => {
              const displayYear = calendarView === 'essene' 
                ? (event.essene_year || event.year) 
                : (event.gregorian_year || event.year);
              return (
                <div
                  key={event.id}
                  className={`timeline-event ${selected?.id === event.id ? 'active' : ''}`}
                  onClick={() => setSelected(event)}
                  title={event.title}
                >
                  <div className="timeline-dot" />
                  <div className="timeline-label">{displayYear}</div>
                </div>
              );
            })}
          </div>
          <div className="scroll-hints">
            <button onClick={() => handleScroll('left')} style={{ flex: 'none' }}><ChevronLeft size={18} /></button>
            <span style={{ margin: 'auto 0' }}>Scroll or use arrows to navigate</span>
            <button onClick={() => handleScroll('right')} style={{ flex: 'none' }}><ChevronRight size={18} /></button>
          </div>
        </div>
      )}

      {selected && (
        <div className="details">
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
            {selected.gregorian_year && (
              <div className="year">
                {selected.gregorian_year} <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Gregorian</span>
              </div>
            )}
            {selected.essene_year && (
              <div className="year">
                {selected.essene_year} <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Essene</span>
              </div>
            )}
            {!selected.gregorian_year && !selected.essene_year && selected.year && (
              <div className="year">{selected.year} AD</div>
            )}
          </div>
          <h2>{selected.title}</h2>
          <p>{selected.description || 'No description provided.'}</p>
          {selected.bible_references && selected.bible_references.length > 0 && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.875rem' }}>
              <strong>References:</strong> {selected.bible_references.join(', ')}
            </div>
          )}
          {selected.category && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.875rem' }}>
              <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', background: '#e2e8f0', borderRadius: '0.25rem', color: '#334155' }}>
                {selected.category}
              </span>
            </div>
          )}
        </div>
      )}

      <div style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '1.5rem' }}>
        <p>💡 <strong>Interactive Features:</strong> Click any point on the timeline to view details. Use zoom controls or scroll to navigate.</p>
      </div>
    </div>
  );
}
