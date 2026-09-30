import React, { useMemo, useState } from 'react';
import { GENEALOGY_INDEX } from '../../utils/chronology';
import { CLASSIFICATION, chip, formatGregorian, sectionLabel, theme } from './shared';

// The genealogy as a family tree: the old viewer's Tree and Lineages tabs in one place. Choosing a
// person opens the same side panel the timeline uses, so the two layouts share one selection.
export default function FamilyTree({ people, selectedPersonId, onSelectPerson }) {
  const byId = useMemo(() => new Map(people.map((p) => [p.id, p])), [people]);
  const [lineage, setLineage] = useState('jesus_line');
  const [expanded, setExpanded] = useState(
    () => new Set(['adam', 'noah', 'shem', 'abraham', 'isaac', 'jacob', 'judah', 'david'])
  );

  // Ancestry of the selected person, Adam first: the path the tree opens to.
  const path = useMemo(() => {
    const out = [];
    let cur = byId.get(selectedPersonId);
    while (cur) {
      out.unshift(cur);
      cur = byId.get(cur.parent_id);
    }
    return out;
  }, [byId, selectedPersonId]);
  const onPath = new Set(path.map((p) => p.id));

  const toggle = (id) =>
    setExpanded((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });

  const inLineage = (p) => lineage === 'all' || p.lineages?.includes(lineage);

  const Node = ({ person, depth }) => {
    const kids = (person.children ?? []).map((id) => byId.get(id)).filter(Boolean);
    const open = expanded.has(person.id) || onPath.has(person.id);
    const selected = person.id === selectedPersonId;
    const cls = CLASSIFICATION[person.data_classification];
    return (
      <div style={{ marginLeft: depth ? '1.1rem' : 0 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.2rem 0.4rem',
            borderRadius: '0.35rem',
            background: selected ? theme.selectedBg : 'transparent',
            opacity: inLineage(person) ? 1 : 0.45,
          }}
        >
          <button
            onClick={() => kids.length && toggle(person.id)}
            style={{
              width: '1rem',
              background: 'none',
              border: 'none',
              cursor: kids.length ? 'pointer' : 'default',
              color: theme.textMuted,
              padding: 0,
            }}
            aria-label={open ? 'Collapse' : 'Expand'}
          >
            {kids.length ? (open ? '▾' : '▸') : '·'}
          </button>
          <button
            onClick={() => onSelectPerson(person.id)}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              color: selected ? theme.primary : theme.text,
              fontWeight: selected || onPath.has(person.id) ? 700 : 500,
              font: 'inherit',
              textAlign: 'left',
            }}
          >
            {person.name}
          </button>
          <span style={{ fontSize: '0.75rem', color: theme.textMuted }}>
            {person.gregorian_year_born != null
              ? `${formatGregorian(person.gregorian_year_born)}${person.gregorian_year_died != null ? ` – ${formatGregorian(person.gregorian_year_died)}` : ''}`
              : ''}
            {cls?.hatched ? ` · ${person.data_classification.toLowerCase()}` : ''}
          </span>
        </div>
        {open && kids.map((k) => <Node key={k.id} person={k} depth={depth + 1} />)}
      </div>
    );
  };

  const root = byId.get('adam');
  return (
    <div
      style={{
        background: theme.bgElevated,
        border: `1px solid ${theme.border}`,
        borderRadius: '0.75rem',
        padding: '1rem 1.25rem',
      }}
    >
      <div style={sectionLabel}>LINEAGE</div>
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <button style={chip(lineage === 'all', '#475569')} onClick={() => setLineage('all')}>
          Everyone
        </button>
        {Object.entries(GENEALOGY_INDEX.lineages).map(([id, l]) => (
          <button
            key={id}
            style={chip(lineage === id, l.color)}
            onClick={() => setLineage(id)}
            title={l.description}
          >
            {l.name}
          </button>
        ))}
      </div>
      {path.length > 1 && (
        <div style={{ fontSize: '0.8rem', color: theme.textMuted, marginBottom: '0.75rem' }}>
          {path.map((p, i) => (
            <span key={p.id}>
              {i > 0 && ' → '}
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
              </button>
            </span>
          ))}
          <span> · {path.length} generations</span>
        </div>
      )}
      <div style={{ maxHeight: '70vh', overflowY: 'auto', fontSize: '0.88rem' }}>
        {root && <Node person={root} depth={0} />}
      </div>
    </div>
  );
}
