import React from 'react';
import { amToGregorian } from '../../utils/chronology';
import { VARIANT_META, CERTAINTY_META, formatGregorian, studyUrl } from './shared';

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
