// Bundle entry for the scripture-link explorer, mounted into docs/content/references.md.
// scripture-links.json is generated from bible-text.db by references/build/export_links.py and
// COMMITTED under docs/data -- bible-text.db is a gitignored build artifact, so CI cannot regenerate
// it. scripts/build-links-index.js copies it beside the pop-up data, and the page fetches it there:
// bundled, its Greek and Hebrew turned to escapes and the script passed 4.8 MB.
import { createRoot } from 'react-dom/client';
import { useEffect, useState } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';
import ScriptureLinks from '../components/ScriptureLinks';

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
  return <ScriptureLinks data={data} />;
}

const container = document.getElementById('references-root');

if (container) {
  createRoot(container).render(
    <ErrorBoundary componentName="Scripture Links">
      <Loader />
    </ErrorBoundary>
  );
}
