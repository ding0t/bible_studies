// Reader-facing scripture-link explorer. The point is not the list of references -- any
// cross-reference tool gives you that -- but WHY each link was made: the method that established
// it, how strongly, and the words the two verses actually share.
import { useMemo, useState } from 'react';

const METHODS = {
  'quotation-greek': {
    label: 'Quotation',
    weight: 'textual fact',
    why: 'Greek on both sides. The New Testament authors read their Old Testament in Greek, so the quotation is literally the same words.',
    verb: ['quotes', 'quoted by'],
  },
  'inner-biblical': {
    label: 'Quotation',
    weight: 'textual fact',
    why: 'Hebrew on both sides, with no translation in between — the Old Testament quoting itself.',
    verb: ['quotes', 'quoted by'],
  },
  'allusion-lemma': {
    label: 'Allusion',
    weight: 'shared rare vocabulary',
    why: 'No shared phrasing. What these passages share is vocabulary that occurs almost nowhere else.',
    verb: ['echoes', 'echoed by'],
  },
  'quotation-hebrew': {
    label: 'Candidate',
    weight: "a translator's judgement",
    why: 'A 19th-century Hebrew New Testament renders this as a quotation. That is an informed reading of the text, not evidence from it — worth checking in Greek.',
    verb: ['may quote', 'may be quoted by'],
  },
};

const theme = {
  fg: 'var(--color-text, #1a1a1a)',
  muted: 'var(--color-text-muted, #666)',
  line: 'var(--color-border, #ddd)',
  panel: 'var(--color-card-bg, #fafafa)',
  accent: 'var(--color-primary, #7a5c2e)',
  mark: 'var(--color-selected-bg, #fff3c4)',
};

function Strength({ method, value, corroborated }) {
  const scale = method === 'allusion-lemma' ? value / 30 : value / 45;
  const filled = Math.max(1, Math.min(5, Math.round(scale * 5)));
  return (
    <span style={{ color: theme.muted, fontSize: '0.85em', whiteSpace: 'nowrap' }}>
      <span aria-hidden="true" style={{ color: theme.accent, letterSpacing: '1px' }}>
        {'●'.repeat(filled)}{'○'.repeat(5 - filled)}
      </span>{' '}
      {corroborated ? 'also in reference lists' : 'not in any reference list'}
    </span>
  );
}

// Highlight the shared span inside the fuller verse, so a reader can see the quotation sitting
// in its context rather than taking the claim on trust.
function WithShared({ text, shared }) {
  if (!text) return null;
  const at = shared ? text.indexOf(shared) : -1;
  if (at < 0) return <span>{text}</span>;
  return (
    <span>
      {text.slice(0, at)}
      <mark style={{ background: theme.mark, color: 'inherit', padding: '0 2px' }}>{shared}</mark>
      {text.slice(at + shared.length)}
    </span>
  );
}

function Connection({ link, texts, direction }) {
  const meta = METHODS[link.m];
  const otherKey = direction === 'from' ? link.t : link.f;
  const other = texts[otherKey] || {};
  const englishRef = direction === 'from' ? link.te : null;
  return (
    <article style={{ borderTop: `1px solid ${theme.line}`, padding: '1rem 0' }}>
      <header style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem 1rem', alignItems: 'baseline' }}>
        <strong style={{ fontSize: '1.05em' }}>
          {meta.verb[direction === 'from' ? 0 : 1]} {otherKey}
        </strong>
        {englishRef && <span style={{ color: theme.muted }}>= {englishRef}</span>}
        <Strength method={link.m} value={link.s} corroborated={link.c} />
      </header>

      {link.sh && (
        <p style={{ margin: '0.6rem 0 0.2rem', color: theme.muted, fontSize: '0.9em' }}>
          Shared wording:
        </p>
      )}
      {other.o && (
        <p lang={/[֐-׿]/.test(other.o) ? 'he' : 'grc'}
           dir={/[֐-׿]/.test(other.o) ? 'rtl' : 'ltr'}
           style={{ margin: '0.2rem 0', lineHeight: 1.7 }}>
          <WithShared text={other.o} shared={link.sh} />
        </p>
      )}
      {other.e && (
        <p style={{ margin: '0.3rem 0', color: theme.muted }}>{other.e}</p>
      )}
      {link.v?.length > 0 && (
        <p style={{ margin: '0.5rem 0 0', fontSize: '0.9em', color: theme.muted }}>
          Dead Sea Scrolls at this verse:{' '}
          {link.v.map((v, i) => (
            <span key={i}>
              {i > 0 && '; '}
              <strong>{v.w}</strong> reads <span dir="rtl">{v.l}</span>{' '}
              <em>({v.n} {v.n === 1 ? 'word' : 'words'} of that verse survive)</em>
            </span>
          ))}
        </p>
      )}
    </article>
  );
}

export default function ScriptureLinks({ data }) {
  const [queryText, setQueryText] = useState('');
  const byRef = useMemo(() => {
    const map = new Map();
    for (const link of data.links) {
      for (const [key, dir] of [[link.f, 'from'], [link.t, 'to']]) {
        if (!map.has(key)) map.set(key, []);
        map.get(key).push({ link, direction: dir });
      }
      if (link.te && link.te !== link.t) {
        if (!map.has(link.te)) map.set(link.te, []);
        map.get(link.te).push({ link, direction: 'to' });
      }
    }
    return map;
  }, [data]);

  const references = useMemo(() => [...byRef.keys()].sort(), [byRef]);
  const needle = queryText.trim().toLowerCase();
  const matches = needle
    ? references.filter((r) => r.toLowerCase().startsWith(needle)).slice(0, 12)
    : [];
  const [selected, setSelected] = useState(null);
  const entries = selected ? byRef.get(selected) || [] : [];
  const leads = (selected && data.leads[selected]) || [];
  const grouped = data.methodOrder
    .map((m) => [m, entries.filter((e) => e.link.m === m)])
    .filter(([, rows]) => rows.length > 0);

  return (
    <div style={{ color: theme.fg }}>
      <label htmlFor="ref-input" style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600 }}>
        Look up a verse
      </label>
      <input
        id="ref-input"
        value={queryText}
        onChange={(e) => { setQueryText(e.target.value); setSelected(null); }}
        placeholder="Heb 10:5 &nbsp;·&nbsp; Rev 21:20 &nbsp;·&nbsp; Isa 53:8"
        style={{
          width: '100%', maxWidth: '26rem', padding: '0.55rem 0.7rem', fontSize: '1rem',
          border: `1px solid ${theme.line}`, borderRadius: '6px',
          background: theme.panel, color: theme.fg,
        }}
      />
      {matches.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0',
                     display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
          {matches.map((r) => (
            <li key={r}>
              <button
                onClick={() => { setSelected(r); setQueryText(r); }}
                style={{
                  border: `1px solid ${theme.line}`, background: theme.panel, color: theme.fg,
                  borderRadius: '999px', padding: '0.25rem 0.7rem', cursor: 'pointer',
                }}
              >{r}</button>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <section style={{ marginTop: '1.5rem' }}>
          <h2 style={{ margin: '0 0 0.3rem' }}>{selected}</h2>
          {texts_of(data, selected)}
          {grouped.length === 0 && (
            <p style={{ color: theme.muted, margin: '0.8rem 0' }}>
              {leads.length > 0
                ? 'No connection could be derived from the texts here — the wording diverges too far. What the tradition has long recorded is below.'
                : 'No connection at this verse.'}
            </p>
          )}
          {grouped.map(([method, rows]) => (
            <section key={method} style={{ marginTop: '1.5rem' }}>
              <h3 style={{ margin: '0 0 0.2rem' }}>
                {METHODS[method].label}{' '}
                <span style={{ fontWeight: 400, color: theme.muted, fontSize: '0.75em' }}>
                  — {METHODS[method].weight}
                </span>
              </h3>
              <p style={{ margin: '0 0 0.4rem', color: theme.muted, fontSize: '0.9em' }}>
                {METHODS[method].why}
              </p>
              {rows.map(({ link, direction }, i) => (
                <Connection key={i} link={link} texts={data.texts} direction={direction} />
              ))}
            </section>
          ))}
          {leads.length > 0 && (
            <section style={{ marginTop: '1.75rem', paddingTop: '0.5rem',
                              borderTop: `2px solid ${theme.line}` }}>
              <h3 style={{ margin: '0 0 0.2rem' }}>
                Traditionally cross-referenced{' '}
                <span style={{ fontWeight: 400, color: theme.muted, fontSize: '0.75em' }}>
                  — what readers have long seen here
                </span>
              </h3>
              <p style={{ margin: '0 0 0.6rem', color: theme.muted, fontSize: '0.9em' }}>
                Inherited rather than derived, so treat these as leads to follow rather than as
                evidence from the text. They reach what a textual method cannot — a passage
                paraphrased rather than quoted still leaves no words to match, but its first hearers
                may have recognised it instantly.
              </p>
              {leads.map((lead) => (
                <article key={lead.r} style={{ borderTop: `1px solid ${theme.line}`,
                                               padding: '0.7rem 0' }}>
                  <strong>{lead.r}</strong>{' '}
                  <span style={{ color: theme.muted, fontSize: '0.85em' }}>
                    cited by {lead.v} reference works
                  </span>
                  {data.texts[lead.r]?.e && (
                    <p style={{ margin: '0.3rem 0 0', color: theme.muted }}>
                      {data.texts[lead.r].e}
                    </p>
                  )}
                </article>
              ))}
            </section>
          )}
        </section>
      )}
    </div>
  );
}

function texts_of(data, ref) {
  const entry = data.texts[ref];
  if (!entry) return null;
  const hebrew = entry.o && /[֐-׿]/.test(entry.o);
  return (
    <>
      {entry.o && (
        <p lang={hebrew ? 'he' : 'grc'} dir={hebrew ? 'rtl' : 'ltr'}
           style={{ lineHeight: 1.7, margin: '0.3rem 0' }}>{entry.o}</p>
      )}
      {entry.e && <p style={{ color: theme.muted, margin: '0.3rem 0' }}>{entry.e}</p>}
    </>
  );
}
