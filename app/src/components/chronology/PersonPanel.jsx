import React, { useEffect, useRef } from 'react';
import { eventsForPerson, VARIANTS } from '../../utils/chronology';
import {
  CLASSIFICATION,
  VARIANT_META,
  formatGregorian,
  sectionLabel,
  studyLinkFor,
  theme,
} from './shared';

const SOURCE_LABEL = {
  genesis: 'Genesis',
  anchor: 'Anchor table',
  archaeology: 'Archaeology',
  milestone: 'Prophecy',
  passion: 'AD 33',
  life: '',
};

// Everything the old Genealogy Viewer's detail tab showed, beside the chart rather than on another
// tab: the name study, both calendars, the events this person is tagged in (from every collection,
// stored once), family links that move the chart, and the people whose lives overlapped theirs.
export default function PersonPanel({
  person,
  people,
  onSelectPerson,
  onSelectEvent,
  onFocusLife,
  onClose,
}) {
  const ref = useRef(null);

  // The site's verse pop-ups scan the page once at load; this panel renders later, so hand its
  // references to the scanner when it changes.
  useEffect(() => {
    if (ref.current && typeof window !== 'undefined') window.theWayPopups?.scan(ref.current);
  }, [person?.id]);

  if (!person) return null;
  const byId = new Map(people.map((p) => [p.id, p]));
  const parent = byId.get(person.parent_id);
  const children = (person.children ?? []).map(
    (id) => byId.get(id) ?? { id, name: id.replace(/_/g, ' ') }
  );
  const events = eventsForPerson(person.id);
  const link = studyLinkFor(person);
  const cls = CLASSIFICATION[person.data_classification];
  const dated = person.zadok_year_born != null && person.zadok_year_died != null;
  const contemporaries = dated
    ? people
        .filter(
          (p) =>
            p.id !== person.id &&
            p.zadok_year_born != null &&
            p.zadok_year_died != null &&
            p.zadok_year_born <= person.zadok_year_died &&
            p.zadok_year_died >= person.zadok_year_born
        )
        .sort((a, b) => a.zadok_year_born - b.zadok_year_born)
    : [];
  // For Adam to Terah the three manuscript traditions disagree; show each side by side.
  const traditions = Object.entries(VARIANTS)
    .map(([id, v]) => [id, v.people[person.id]])
    .filter(([, rec]) => rec);

  const box = {
    background: theme.cardBg,
    border: `1px solid ${theme.border}`,
    borderRadius: '0.5rem',
    padding: '0.75rem 0.9rem',
    marginBottom: '0.75rem',
  };
  const linkBtn = {
    background: 'none',
    border: 'none',
    padding: 0,
    color: theme.primary,
    cursor: 'pointer',
    font: 'inherit',
    textAlign: 'left',
  };

  return (
    <aside
      ref={ref}
      style={{
        flex: '0 1 360px',
        minWidth: '300px',
        maxHeight: '80vh',
        overflowY: 'auto',
        background: theme.bgElevated,
        border: `1px solid ${theme.border}`,
        borderRadius: '0.75rem',
        padding: '1rem 1.1rem',
        fontSize: '0.88rem',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: '0.5rem',
        }}
      >
        <h3 style={{ margin: 0 }}>{person.name}</h3>
        <button onClick={onClose} style={{ ...linkBtn, color: theme.textMuted }} aria-label="Close">
          ✕
        </button>
      </div>
      {person.title && (
        <div style={{ color: theme.textMuted, marginBottom: '0.6rem' }}>{person.title}</div>
      )}

      {person.name_hebrew && (
        <div style={{ ...box, borderLeft: '4px solid #4f46e5' }}>
          <span dir="rtl" lang="he" style={{ fontFamily: 'serif', fontSize: '1.4em' }}>
            {person.name_hebrew}
          </span>
          <div style={{ color: '#4f46e5', fontWeight: 600 }}>{person.name_transliteration}</div>
          {person.name_meaning && (
            <div style={{ color: theme.textMuted, fontStyle: 'italic' }}>{person.name_meaning}</div>
          )}
        </div>
      )}

      <div style={box}>
        {dated ? (
          <>
            <div>
              <strong>{formatGregorian(person.gregorian_year_born)}</strong> –{' '}
              <strong>{formatGregorian(person.gregorian_year_died)}</strong>
              {person.lifespan_years != null && ` · ${person.lifespan_years} years`}
            </div>
            <div style={{ color: theme.textMuted }}>
              AM {person.zadok_year_born} – {person.zadok_year_died}
            </div>
          </>
        ) : (
          <div style={{ color: theme.textMuted }}>Scripture gives no years for this person.</div>
        )}
        {cls && (
          <div style={{ marginTop: '0.35rem', fontSize: '0.8rem' }}>
            <span style={{ fontWeight: 700 }}>{person.data_classification}</span> · {cls.label}
          </div>
        )}
        {traditions.length > 1 && (
          <table style={{ marginTop: '0.5rem', fontSize: '0.78rem', borderCollapse: 'collapse' }}>
            <tbody>
              {traditions.map(([id, rec]) => (
                <tr key={id}>
                  <td style={{ paddingRight: '0.6rem', color: VARIANT_META[id]?.color }}>
                    {VARIANT_META[id]?.label.replace(/ \(.*\)/, '')}
                  </td>
                  <td style={{ paddingRight: '0.6rem' }}>
                    born {formatGregorian(rec.gregorian_year_born)} (AM {rec.zadok_year_born})
                  </td>
                  <td>{rec.lifespan_years} years</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {link && (
          <a
            href={link.url}
            style={{ display: 'block', marginTop: '0.5rem', color: theme.primary }}
          >
            {link.label} →
          </a>
        )}
        {dated && (
          <button style={{ ...linkBtn, marginTop: '0.35rem' }} onClick={() => onFocusLife(person)}>
            Zoom the chart to this life
          </button>
        )}
      </div>

      <div style={sectionLabel}>FAMILY</div>
      <div style={box}>
        {parent ? (
          <div>
            Parent:{' '}
            <button style={linkBtn} onClick={() => onSelectPerson(parent.id)}>
              {parent.name}
            </button>
          </div>
        ) : (
          <div style={{ color: theme.textMuted }}>No parent recorded in this dataset.</div>
        )}
        {children.length > 0 && (
          <div style={{ marginTop: '0.3rem' }}>
            Children:{' '}
            {children.map((c, i) => (
              <span key={c.id}>
                {i > 0 && ', '}
                {byId.has(c.id) ? (
                  <button style={linkBtn} onClick={() => onSelectPerson(c.id)}>
                    {c.name}
                  </button>
                ) : (
                  <span style={{ textTransform: 'capitalize' }}>{c.name}</span>
                )}
              </span>
            ))}
          </div>
        )}
      </div>

      <div style={sectionLabel}>EVENTS ({events.length})</div>
      <div style={box}>
        {events.length === 0 && <div style={{ color: theme.textMuted }}>None recorded.</div>}
        {events.map((e) => (
          <div key={`${e.source}-${e.id}`} style={{ marginBottom: '0.45rem' }}>
            <button style={{ ...linkBtn, fontWeight: 600 }} onClick={() => onSelectEvent(e)}>
              {e.label}
            </button>
            <div style={{ color: theme.textMuted, fontSize: '0.8rem' }}>
              {e.am == null ? 'undated' : `${formatGregorian(e.gregorian)} · AM ${e.am}`}
              {SOURCE_LABEL[e.source] ? ` · ${SOURCE_LABEL[e.source]}` : ''}
              {e.refs ? ` · ${e.refs}` : ''}
            </div>
          </div>
        ))}
      </div>

      {contemporaries.length > 0 && (
        <>
          <div style={sectionLabel}>ALIVE AT THE SAME TIME ({contemporaries.length})</div>
          <div style={{ ...box, lineHeight: 1.7 }}>
            {contemporaries.map((c, i) => (
              <span key={c.id}>
                {i > 0 && ' · '}
                <button style={linkBtn} onClick={() => onSelectPerson(c.id)}>
                  {c.name}
                </button>
              </span>
            ))}
          </div>
        </>
      )}

      {person.bible_references?.length > 0 && (
        <>
          <div style={sectionLabel}>SCRIPTURE</div>
          <div style={box}>
            {person.bible_references.map((r) => (
              <div key={r}>{r}</div>
            ))}
          </div>
        </>
      )}
    </aside>
  );
}
