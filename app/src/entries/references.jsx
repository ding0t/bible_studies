// Bundle entry for the scripture-link explorer, mounted into docs/content/references.md.
// scripture-links.json is generated from bible-text.db by references/build/export_links.py and
// COMMITTED under docs/data -- bible-text.db is a gitignored build artifact, so CI cannot regenerate
// it. scripts/build-links-index.js copies it beside the pop-up data, and the page fetches it there:
// bundled, its Greek and Hebrew turned to escapes and the script passed 4.8 MB.
import { createRoot } from 'react-dom/client';
import { useEffect, useState } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';
import ScriptureLinks from '../components/ScriptureLinks';
import { ConfirmationCurve, KeyCoverage, RuleAgreement, RuleProfiles, TrustMap } from '../components/MethodCharts';
import { RULES } from '../utils/scriptureLinks.js';
// What each rule finds and how often it is confirmed: a few kilobytes, so bundled rather than fetched.
import method from '../../../docs/data/link-method.json';

const DATA = new URL('../popups/scripture-links.json', import.meta.url);

function Loader() {
  const [data, setData] = useState(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    fetch(DATA)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then(setData)
      .catch(() => setFailed(true));
  }, []);
  if (failed) return <p>The scripture links could not be loaded. Try reloading the page.</p>;
  if (!data) return <p aria-live="polite">Loading the scripture links…</p>;
  return <ScriptureLinks data={data} method={method} />;
}

// The method page (about/how-we-cross-reference.md) places the same charts beside its prose:
// <div data-link-chart="trust"></div> and so on. A verse they name opens on the Scripture Links page.
const openOnLinksPage = (ref) => { window.location.href = `/references/#ref=${encodeURIComponent(ref)}`; };
const CHARTS = {
  curve: () => <ConfirmationCurve method={method} />,
  trust: () => <TrustMap method={method} />,
  'profiles-nt': () => <RuleProfiles method={method} onOpen={openOnLinksPage} rules={RULES.filter((r) => r.method !== 'inner-biblical')} />,
  'profiles-ot': () => <RuleProfiles method={method} onOpen={openOnLinksPage} rules={RULES.filter((r) => r.method === 'inner-biblical')} />,
  'agree-nt': () => <RuleAgreement method={method} scope="nt" />,
  'agree-ot': () => <RuleAgreement method={method} scope="ot" />,
  'key-nt': () => <KeyCoverage method={method} scope="nt" onOpen={openOnLinksPage} />,
  'key-ot': () => <KeyCoverage method={method} scope="ot" onOpen={openOnLinksPage} />,
};
for (const el of document.querySelectorAll('[data-link-chart]')) {
  const Chart = CHARTS[el.dataset.linkChart];
  if (Chart) {
    createRoot(el).render(
      <ErrorBoundary componentName="Method chart">
        <Chart />
      </ErrorBoundary>
    );
  }
}

const container = document.getElementById('references-root');

if (container) {
  createRoot(container).render(
    <ErrorBoundary componentName="Scripture Links">
      <Loader />
    </ErrorBoundary>
  );
}
