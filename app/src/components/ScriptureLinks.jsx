// Reader-facing scripture-link explorer. The point is not the list of references -- any
// cross-reference tool gives you that -- but WHY each link was made: the method that established
// it, how strongly, and the words the two verses actually share. Four views of one set of links:
// the lookup, a chord map of the books, a book-by-book table, and the shape of the evidence. The
// address bar holds the view and the verse (#ref=Heb 10:5, #view=map&scope=ot-ot) so any of them
// can be shared, and the back button walks the verses a reader has followed.
import { useCallback, useEffect, useMemo, useState } from 'react';
import { ChordMap, EgoGraph, MatrixTable, MethodBars, MethodKey, TopVerses } from './LinkCharts.jsx';
import { KeyCoverage, RuleAgreement, RuleProfiles, TrustMap } from './MethodCharts.jsx';
import {
  METHODS,
  METHOD_NAMES,
  SCOPES,
  RULES,
  basisWords,
  bookOfKey,
  calibration,
  confirmationFor,
  displayBook as bookName,
  entriesFor,
  indexByRef,
  inScope,
  lookupKey,
  prettyKey,
  startingPoints,
} from '../utils/scriptureLinks.js';

const theme = {
  fg: 'var(--color-text, #1a1a1a)',
  muted: 'var(--color-text-muted, #666)',
  line: 'var(--color-border, #ddd)',
  panel: 'var(--color-card-bg, #fafafa)',
  accent: 'var(--color-primary, #7a5c2e)',
  mark: 'var(--color-selected-bg, #fff3c4)',
};

const VIEWS = [
  { id: 'lookup', label: 'Look up a verse' },
  { id: 'map', label: 'Map of the books' },
  { id: 'table', label: 'Book by book' },
  { id: 'shape', label: 'The evidence' },
];

const chip = (on) => ({
  border: `1px solid ${on ? theme.accent : theme.line}`,
  background: on ? theme.accent : theme.panel,
  color: on ? 'var(--md-primary-bg-color, #fff)' : theme.fg,
  borderRadius: '999px',
  padding: '0.3rem 0.8rem',
  cursor: 'pointer',
  font: 'inherit',
  fontSize: '0.9rem',
});

const link = { background: 'none', border: 0, padding: 0, color: theme.accent, cursor: 'pointer', font: 'inherit', textDecoration: 'underline' };

function readHash() {
  if (typeof window === 'undefined') return {};
  return Object.fromEntries(new window.URLSearchParams(window.location.hash.replace(/^#/, '')));
}

// How far to trust a link, calibrated: the share of links found the same way that an outside list
// confirms. A score on its own (alignment 24, weight 15) means nothing to a reader; this does.
function Trust({ link, cal }) {
  const t = confirmationFor(cal, link);
  const rate = t.n ? t.c / t.n : 0;
  const colour = METHODS[link.m]?.color ?? theme.accent;
  return (
    <span style={{ color: theme.muted, fontSize: '0.85em', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
      <svg width="54" height="8" aria-hidden="true">
        <rect width="54" height="8" rx="4" fill={theme.line} />
        <rect width={Math.max(3, rate * 54)} height="8" rx="4" fill={colour} />
      </svg>
      <span title={`${t.c} of ${t.n} links found ${t.exact ? 'this way' : 'by this kind of evidence'} are confirmed by an outside list`}>
        {Math.round(rate * 100)}% of links found {t.exact ? 'this way' : 'like this'} are confirmed
      </span>
      <span>· {link.c ? 'this one is in a reference list' : 'this one is in no reference list'}</span>
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

function Connection({ link: l, texts, direction, at, showAt, onOpen, cal }) {
  const meta = METHODS[l.m];
  const otherKey = direction === 'from' ? l.t : l.f;
  const other = texts[otherKey] || {};
  const englishRef = direction === 'from' ? l.te : null;
  return (
    <article style={{ borderTop: `1px solid ${theme.line}`, padding: '1rem 0' }}>
      <header style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem 1rem', alignItems: 'baseline' }}>
        <strong style={{ fontSize: '1.05em' }}>
          {showAt && <span style={{ color: theme.muted, fontWeight: 400 }}>{prettyKey(at)} </span>}
          {meta.verb[direction === 'from' ? 0 : 1]}{' '}
          <button type="button" onClick={() => onOpen(otherKey)} style={{ ...link, fontWeight: 700, fontSize: 'inherit' }}>
            {prettyKey(otherKey)}
          </button>
        </strong>
        {englishRef && <span style={{ color: theme.muted }}>= {englishRef}</span>}
        <Trust link={l} cal={cal} />
      </header>

      {basisWords(l.b).length > 0 && (
        <p style={{ margin: '0.35rem 0 0', color: theme.muted, fontSize: '0.85em' }}>
          Found by: {basisWords(l.b).join('; ')}.
        </p>
      )}
      {l.sh && <p style={{ margin: '0.6rem 0 0.2rem', color: theme.muted, fontSize: '0.9em' }}>Shared wording:</p>}
      {other.o && (
        <p lang={/[֐-׿]/.test(other.o) ? 'he' : 'grc'} dir={/[֐-׿]/.test(other.o) ? 'rtl' : 'ltr'} style={{ margin: '0.2rem 0', lineHeight: 1.7 }}>
          <WithShared text={other.o} shared={l.sh} />
        </p>
      )}
      {other.e && <p style={{ margin: '0.3rem 0', color: theme.muted }}>{other.e}</p>}
      {l.v?.length > 0 && (
        <p style={{ margin: '0.5rem 0 0', fontSize: '0.9em', color: theme.muted }}>
          Dead Sea Scrolls at this verse:{' '}
          {l.v.map((v, i) => (
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

function Scope({ scope, setScope, links, fresh, setFresh }) {
  return (
    <div role="group" aria-label="Which links to draw" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center', margin: '0.5rem 0 1rem' }}>
      {SCOPES.map((s) => (
        <button key={s.id} type="button" aria-pressed={scope === s.id} onClick={() => setScope(s.id)} style={chip(scope === s.id)}>
          {s.label} <span style={{ opacity: 0.75 }}>({links.filter((l) => inScope(l, s.id) && (!fresh || !l.c)).length})</span>
        </button>
      ))}
      <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.9rem', marginLeft: '0.4rem', cursor: 'pointer' }}>
        <input type="checkbox" checked={fresh} onChange={(e) => setFresh(e.target.checked)} />
        Only links no reference list carries
      </label>
    </div>
  );
}

// What a selected book or pair of books holds, each link one step from the lookup.
function FlowList({ links, active, onOpen, clear }) {
  if (!active) {
    return <p style={{ color: theme.muted, fontSize: '0.9rem' }}>Select a book or a pair of books to list the links between them.</p>;
  }
  const mine = links
    .filter((l) => (active.book ? bookOfKey(l.f) === active.book || bookOfKey(l.t) === active.book : bookOfKey(l.f) === active.from && bookOfKey(l.t) === active.to))
    .sort((a, b) => a.m.localeCompare(b.m) || a.f.localeCompare(b.f));
  const heading = active.book ? bookName(active.book) : `${bookName(active.from)} to ${bookName(active.to)}`;
  return (
    <section aria-live="polite" style={{ borderTop: `2px solid ${theme.line}`, marginTop: '1rem', paddingTop: '0.6rem' }}>
      <h3 style={{ margin: '0 0 0.4rem' }}>
        {heading} <span style={{ fontWeight: 400, color: theme.muted, fontSize: '0.8em' }}>{mine.length} link{mine.length === 1 ? '' : 's'}</span>{' '}
        <button type="button" onClick={clear} style={{ ...link, fontSize: '0.8rem' }}>clear</button>
      </h3>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, columns: '16rem auto', fontSize: '0.9rem' }}>
        {mine.slice(0, 120).map((l, i) => (
          <li key={i} style={{ breakInside: 'avoid', padding: '0.15rem 0' }}>
            <button type="button" onClick={() => onOpen(l.f)} style={link}>{prettyKey(l.f)}</button>
            <span style={{ color: METHODS[l.m]?.color }}> {METHODS[l.m]?.verb[0]} </span>
            <button type="button" onClick={() => onOpen(l.t)} style={link}>{prettyKey(l.t)}</button>
            <span style={{ color: theme.muted }}> · {METHOD_NAMES[l.m]}</span>
          </li>
        ))}
      </ul>
      {mine.length > 120 && <p style={{ color: theme.muted, fontSize: '0.85rem' }}>First 120 of {mine.length}.</p>}
    </section>
  );
}

export default function ScriptureLinks({ data, method }) {
  const initial = useMemo(readHash, []);
  const [view, setView] = useState(VIEWS.some((v) => v.id === initial.view) ? initial.view : 'lookup');
  const [scope, setScope] = useState(SCOPES.some((s) => s.id === initial.scope) ? initial.scope : 'nt-ot');
  const [queryText, setQueryText] = useState(initial.ref ?? '');
  const [selected, setSelected] = useState(() => (initial.ref ? lookupKey(initial.ref) : null));
  const [hidden, setHidden] = useState(() => new Set());
  const [active, setActive] = useState(null);
  const [trail, setTrail] = useState([]);
  const [fresh, setFresh] = useState(initial.fresh === '1');

  const byRef = useMemo(() => indexByRef(data.links), [data]);
  const references = useMemo(() => [...byRef.keys()].sort(), [byRef]);
  const scoped = useMemo(() => data.links.filter((l) => inScope(l, scope) && (!fresh || !l.c)), [data, scope, fresh]);
  const cal = useMemo(() => calibration(data.links), [data]);
  const starts = useMemo(() => startingPoints(data.links), [data]);

  const open = useCallback((text, push = true) => {
    const target = lookupKey(text);
    if (!target) return;
    setSelected(target);
    setQueryText(target.label);
    setView('lookup');
    setTrail((t) => (t.at(-1) === target.label ? t : [...t, target.label].slice(-8)));
    if (push) {
      const params = new window.URLSearchParams(window.location.hash.replace(/^#/, ''));
      params.set('ref', target.key ?? target.chapter);
      params.delete('view');
      window.history.pushState(null, '', `#${params}`);
    }
  }, []);

  useEffect(() => {
    const onHash = () => {
      const h = readHash();
      if (VIEWS.some((v) => v.id === h.view)) setView(h.view);
      if (h.ref) open(h.ref, false);
    };
    window.addEventListener('popstate', onHash);
    return () => window.removeEventListener('popstate', onHash);
  }, [open]);

  const chooseView = (id) => {
    setView(id);
    const params = new window.URLSearchParams(window.location.hash.replace(/^#/, ''));
    if (id === 'lookup') params.delete('view'); else params.set('view', id);
    window.history.replaceState(null, '', `#${params}`);
  };
  const chooseFresh = (on) => {
    setFresh(on);
    setActive(null);
    const params = new window.URLSearchParams(window.location.hash.replace(/^#/, ''));
    if (on) params.set('fresh', '1'); else params.delete('fresh');
    window.history.replaceState(null, '', `#${params}`);
  };
  const chooseScope = (id) => {
    setScope(id);
    setActive(null);
    const params = new window.URLSearchParams(window.location.hash.replace(/^#/, ''));
    params.set('scope', id);
    window.history.replaceState(null, '', `#${params}`);
  };

  const needle = queryText.trim().toLowerCase();
  const parsed = lookupKey(queryText);
  const suggestions = useMemo(() => {
    if (!needle || (selected && queryText === selected.label)) return [];
    if (parsed?.chapter) return references.filter((r) => r.startsWith(`${parsed.chapter}:`)).slice(0, 14);
    if (parsed?.key) return references.filter((r) => r === parsed.key);
    return references.filter((r) => prettyKey(r).toLowerCase().startsWith(needle) || r.toLowerCase().startsWith(needle)).slice(0, 12);
  }, [needle, parsed, references, selected, queryText]);

  const entries = selected ? entriesFor(byRef, selected).filter((e) => !hidden.has(e.link.m)) : [];
  const leads = (selected?.key && data.leads[selected.key]) || [];
  const noted = (selected?.key && data.noted?.[selected.key]) || [];
  const grouped = data.methodOrder
    .map((m) => [m, entries.filter((e) => e.link.m === m)])
    .filter(([, rows]) => rows.length > 0);
  const present = data.methodOrder.filter((m) => selected && entriesFor(byRef, selected).some((e) => e.link.m === m));
  const showText = selected?.key ? data.texts[selected.key] : null;
  const surprise = () => open(references[Math.floor(Math.random() * references.length)]);

  return (
    <div style={{ color: theme.fg }}>
      <div role="tablist" aria-label="Ways to explore the links" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.2rem' }}>
        {VIEWS.map((v) => (
          <button key={v.id} type="button" role="tab" aria-selected={view === v.id} onClick={() => chooseView(v.id)} style={chip(view === v.id)}>
            {v.label}
          </button>
        ))}
      </div>

      {view === 'lookup' && (
        <>
          <form onSubmit={(e) => { e.preventDefault(); if (parsed) open(queryText); }} role="search">
            <label htmlFor="ref-input" style={{ display: 'block', marginBottom: '0.4rem', fontWeight: 600 }}>Look up a verse or a chapter</label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <input
                id="ref-input"
                value={queryText}
                onChange={(e) => { setQueryText(e.target.value); }}
                placeholder="Hebrews 10:5 · Rev 21:20 · Isaiah 53"
                autoComplete="off"
                aria-describedby="ref-help"
                style={{ flex: '1 1 16rem', maxWidth: '26rem', padding: '0.55rem 0.7rem', fontSize: '1rem', border: `1px solid ${theme.line}`, borderRadius: '6px', background: theme.panel, color: theme.fg }}
              />
              <button type="submit" style={chip(true)} disabled={!parsed}>Show connections</button>
              <button type="button" onClick={surprise} style={chip(false)}>Surprise me</button>
            </div>
            <p id="ref-help" style={{ margin: '0.4rem 0 0', fontSize: '0.85rem', color: theme.muted }}>
              Full names or abbreviations both work. A chapter alone lists every linked verse in it.
            </p>
          </form>

          {suggestions.length > 0 && (
            <ul aria-label="Linked verses" style={{ listStyle: 'none', padding: 0, margin: '0.6rem 0 0', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {suggestions.map((r) => (
                <li key={r}><button type="button" onClick={() => open(r)} style={chip(false)}>{prettyKey(r)}</button></li>
              ))}
            </ul>
          )}
          {needle && parsed && !suggestions.length && !(selected && queryText === selected.label) && (
            <p style={{ color: theme.muted, fontSize: '0.9rem' }}>No derived connection at {parsed.label}. <button type="button" onClick={() => open(queryText)} style={link}>Show it anyway</button> for the traditional cross-references.</p>
          )}

          {!selected && (
            <section style={{ marginTop: '1.4rem' }}>
              <h2 style={{ margin: '0 0 0.4rem', fontSize: '1.1rem' }}>Not sure where to start?</h2>
              <p style={{ margin: '0 0 0.5rem', color: theme.muted, fontSize: '0.9rem' }}>
                These New Testament verses quote or echo the Old, and include links no reference list carries.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {starts.map((r) => <li key={r}><button type="button" onClick={() => open(r)} style={chip(false)}>{prettyKey(r)}</button></li>)}
              </ul>
              <p style={{ margin: '1rem 0 0', fontSize: '0.9rem' }}>
                Or see the whole picture first:{' '}
                <button type="button" onClick={() => chooseView('map')} style={link}>the map of the books</button>,{' '}
                <button type="button" onClick={() => chooseView('table')} style={link}>book by book</button>,{' '}
                <button type="button" onClick={() => chooseView('shape')} style={link}>the evidence</button>.
              </p>
            </section>
          )}

          {trail.length > 1 && (
            <nav aria-label="Verses you have followed" style={{ margin: '1rem 0 0', fontSize: '0.85rem', color: theme.muted }}>
              Followed:{' '}
              {trail.map((t, i) => (
                <span key={`${t}-${i}`}>
                  {i > 0 && ' → '}
                  {i === trail.length - 1 ? <strong>{t}</strong> : <button type="button" onClick={() => open(t)} style={link}>{t}</button>}
                </span>
              ))}
            </nav>
          )}

          {selected && (
            <section style={{ marginTop: '1.5rem' }}>
              <h2 style={{ margin: '0 0 0.3rem' }}>{selected.label}</h2>
              {showText?.o && (
                <p lang={/[֐-׿]/.test(showText.o) ? 'he' : 'grc'} dir={/[֐-׿]/.test(showText.o) ? 'rtl' : 'ltr'} style={{ lineHeight: 1.7, margin: '0.3rem 0' }}>{showText.o}</p>
              )}
              {showText?.e && <p style={{ color: theme.muted, margin: '0.3rem 0' }}>{showText.e}</p>}

              {present.length > 1 && (
                <div role="group" aria-label="Show these kinds of link" style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', margin: '0.8rem 0' }}>
                  {present.map((m) => (
                    <button key={m} type="button" aria-pressed={!hidden.has(m)} style={chip(!hidden.has(m))}
                      onClick={() => setHidden((h) => { const n = new Set(h); if (n.has(m)) n.delete(m); else n.add(m); return n; })}>
                      {METHOD_NAMES[m]}
                    </button>
                  ))}
                </div>
              )}

              <p role="status" style={{ color: theme.muted, fontSize: '0.9rem', margin: '0.4rem 0' }}>
                {entries.length} connection{entries.length === 1 ? '' : 's'} at {selected.label}.
              </p>
              <EgoGraph label={selected.label} entries={entries} onOpen={open} />
              <MethodKey methods={present} />

              {grouped.length === 0 && (
                <p style={{ color: theme.muted, margin: '0.8rem 0' }}>
                  {leads.length > 0
                    ? 'No connection could be derived from the texts here: the wording diverges too far. What the tradition has long recorded is below.'
                    : 'No connection at this verse.'}
                </p>
              )}
              {grouped.map(([method, rows]) => (
                <section key={method} style={{ marginTop: '1.5rem' }}>
                  <h3 style={{ margin: '0 0 0.2rem' }}>
                    {METHODS[method].label}{' '}
                    <span style={{ fontWeight: 400, color: theme.muted, fontSize: '0.75em' }}>{METHODS[method].weight}</span>
                  </h3>
                  <p style={{ margin: '0 0 0.4rem', color: theme.muted, fontSize: '0.9em' }}>{METHODS[method].why}</p>
                  {rows.map(({ link: l, direction, at }, i) => (
                    <Connection key={i} link={l} texts={data.texts} direction={direction} at={at} showAt={Boolean(selected.chapter)} onOpen={open} cal={cal} />
                  ))}
                </section>
              ))}
              {noted.length > 0 && (
                <section style={{ marginTop: '1.75rem', paddingTop: '0.5rem', borderTop: `2px solid ${theme.line}` }}>
                  <h3 style={{ margin: '0 0 0.2rem' }}>
                    Named as a quotation{' '}
                    <span style={{ fontWeight: 400, color: theme.muted, fontSize: '0.75em' }}>by unfoldingWord’s Translation Notes</span>
                  </h3>
                  <p style={{ margin: '0 0 0.6rem', color: theme.muted, fontSize: '0.9em' }}>
                    The notes’ editors say this verse quotes the passage below, and the texts alone do not show it strongly enough
                    to derive. A stated judgement to check against both verses.
                  </p>
                  {noted.map((r) => (
                    <article key={r} style={{ borderTop: `1px solid ${theme.line}`, padding: '0.7rem 0' }}>
                      <button type="button" onClick={() => open(r)} style={{ ...link, fontWeight: 700 }}>{prettyKey(r)}</button>
                      {data.texts[r]?.e && <p style={{ margin: '0.3rem 0 0', color: theme.muted }}>{data.texts[r].e}</p>}
                    </article>
                  ))}
                </section>
              )}
              {leads.length > 0 && (
                <section style={{ marginTop: '1.75rem', paddingTop: '0.5rem', borderTop: `2px solid ${theme.line}` }}>
                  <h3 style={{ margin: '0 0 0.2rem' }}>
                    Traditionally cross-referenced{' '}
                    <span style={{ fontWeight: 400, color: theme.muted, fontSize: '0.75em' }}>what readers have long seen here</span>
                  </h3>
                  <p style={{ margin: '0 0 0.6rem', color: theme.muted, fontSize: '0.9em' }}>
                    Inherited, so treat these as leads to follow and not as evidence from the text. They reach what a textual method
                    cannot: a passage paraphrased leaves no words to match, but its first hearers may have recognised it instantly.
                  </p>
                  {leads.map((lead) => (
                    <article key={lead.r} style={{ borderTop: `1px solid ${theme.line}`, padding: '0.7rem 0' }}>
                      <button type="button" onClick={() => open(lead.r)} style={{ ...link, fontWeight: 700 }}>{prettyKey(lead.r)}</button>{' '}
                      <span style={{ color: theme.muted, fontSize: '0.85em' }}>cited by {lead.v} reference works</span>
                      {data.texts[lead.r]?.e && <p style={{ margin: '0.3rem 0 0', color: theme.muted }}>{data.texts[lead.r].e}</p>}
                    </article>
                  ))}
                </section>
              )}
            </section>
          )}
        </>
      )}

      {view === 'map' && (
        <section>
          <h2 style={{ margin: '0 0 0.3rem' }}>The map of the books</h2>
          <p style={{ color: theme.muted, margin: '0 0 0.2rem', fontSize: '0.95rem' }}>
            Each curve joins two books where a verse in one quotes or echoes a verse in the other. The wider the curve, the more verses it carries.
          </p>
          <Scope scope={scope} setScope={chooseScope} links={data.links} fresh={fresh} setFresh={chooseFresh} />
          <MethodKey methods={data.methodOrder.filter((m) => scoped.some((l) => l.m === m))} />
          <ChordMap links={scoped} active={active} setActive={setActive} />
          <FlowList links={scoped} active={active} onOpen={open} clear={() => setActive(null)} />
        </section>
      )}

      {view === 'table' && (
        <section>
          <h2 style={{ margin: '0 0 0.3rem' }}>Book by book</h2>
          <p style={{ color: theme.muted, margin: '0 0 0.2rem', fontSize: '0.95rem' }}>
            The same links as a table, for reading an exact count. Darker is more links.
          </p>
          <Scope scope={scope} setScope={chooseScope} links={data.links} fresh={fresh} setFresh={chooseFresh} />
          <MatrixTable links={scoped} active={active} setActive={setActive} />
          <FlowList links={scoped} active={active} onOpen={open} clear={() => setActive(null)} />
        </section>
      )}

      {view === 'shape' && (
        <section>
          <h2 style={{ margin: '0 0 0.3rem' }}>The evidence</h2>
          <p style={{ color: theme.muted, margin: '0 0 0.2rem', fontSize: '0.95rem' }}>
            How many links rest on each kind of evidence, and which verses the rest of Scripture returns to.
          </p>
          <Scope scope={scope} setScope={chooseScope} links={data.links} fresh={fresh} setFresh={chooseFresh} />
          <MethodBars links={scoped} methodOrder={data.methodOrder} />
          <h3 style={{ margin: '1.6rem 0 0.4rem' }}>Most often drawn on</h3>
          <TopVerses links={scoped} onOpen={open} />
          {method && (
            <>
              <h3 style={{ margin: '2rem 0 0.3rem' }}>How far to trust each rule, and what it adds</h3>
              <p style={{ color: theme.muted, margin: '0 0 0.2rem', fontSize: '0.9rem' }}>
                Every link names the rule that found it. Here is each rule’s record against outside lists and answer keys.
              </p>
              <TrustMap method={method} />
              <RuleProfiles method={method} onOpen={open} rules={RULES.filter((r) => (scope === 'ot-ot') === (r.method === 'inner-biblical') || scope === 'all')} />
              <h3 style={{ margin: '1.6rem 0 0.3rem' }}>Where the rules agree</h3>
              <RuleAgreement method={method} scope={scope === 'ot-ot' ? 'ot' : 'nt'} />
              <h3 style={{ margin: '1.6rem 0 0.3rem' }}>What the rules miss</h3>
              <p style={{ color: theme.muted, margin: '0 0 0.2rem', fontSize: '0.9rem' }}>
                {scope === 'ot-ot'
                  ? 'Every verse of sixteen well-known Old Testament parallels, one square each.'
                  : 'Every quotation the WEB translators’ footnotes or unfoldingWord’s Translation Notes name, one square each.'}
              </p>
              <KeyCoverage method={method} scope={scope === 'ot-ot' ? 'ot' : 'nt'} onOpen={open} />
            </>
          )}
        </section>
      )}

      <p style={{ marginTop: '2rem', fontSize: '0.8rem', color: theme.muted }}>
        {data.links.length} links, exported {data.generated}. The diagrams are drawn from the same data as the lookup and change when it is re-exported.
      </p>
    </div>
  );
}
