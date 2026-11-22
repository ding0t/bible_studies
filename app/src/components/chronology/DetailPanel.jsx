import React from 'react';
import { amToGregorian, CHRONOLOGY } from '../../utils/chronology';
import { VARIANT_META, CERTAINTY_META, formatGregorian, studyUrl } from './shared';
import Harmony from './Harmony';

const RECORDS = new Map([...CHRONOLOGY.artifacts, ...CHRONOLOGY.anchors].map((a) => [a.id, a]));
const ROOTS = new Map(CHRONOLOGY.dating_roots.map((r) => [r.id, r]));
const JOB_LABEL = { fix: 'fixes the year', check: 'checks it', confirm: 'confirms the event', limit: 'sets a limit', rival: 'a rival date' };

// An anchor row names the outside record its year rests on and the witnesses that bear on it.
function DatedBy({ selected, theme }) {
  const root = ROOTS.get(selected.dated_by);
  const witnesses = (selected.witnesses ?? []).filter((w) => RECORDS.has(w.id));
  if (!root && !witnesses.length) return null;
  return (
    <div style={{ fontSize: '0.85rem', color: theme.textMuted, margin: '0.4rem 0' }}>
      {root && (
        <div>
          Dated by {root.label}: {root.record}
          {root.sky ? ` · ${root.sky}` : ''}
        </div>
      )}
      {witnesses.length > 0 && (
        <div>
          Witnesses:{' '}
          {witnesses.map((w, i) => (
            <span key={w.id}>
              {i ? '; ' : ''}
              {RECORDS.get(w.id).label} ({JOB_LABEL[w.job]})
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DetailPanel({ selected, theme, activeEpochs, markerDate }) {
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
            {selected.tier && selected.error && ` ${selected.error}`}
            {selected.scripture && ` · ${selected.scripture}`}
          </div>
          <DatedBy selected={selected} theme={theme} />
          {selected.image && (
            <img
              src={selected.image}
              alt={selected.label}
              style={{ maxWidth: '100%', maxHeight: '12rem', borderRadius: '0.4rem', margin: '0.3rem 0' }}
            />
          )}
          <Harmony refs={selected.scripture} theme={theme} />
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
          <Harmony refs={selected.refs} theme={theme} />
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
