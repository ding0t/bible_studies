import React from 'react';
import { harmonyFor } from '../../utils/chronology';

// The other gospels' accounts of the event a panel shows, from STEP's harmony. Plain text, so the
// site-wide pop-up opens each reference like any other on the page.
export default function Harmony({ refs, theme }) {
  const found = harmonyFor(refs);
  if (!found.length) return null;
  return (
    <div style={{ fontSize: '0.85rem', color: theme.textMuted, margin: '0.4rem 0' }}>
      {found.map((h) => (
        <div key={h.label}>
          Also told in {h.others.join('; ')}{' '}
          <span title="STEP Bible's Harmony of the Gospels (STEPBible.org, Tyndale House)">({h.label}, STEP harmony)</span>
        </div>
      ))}
    </div>
  );
}
