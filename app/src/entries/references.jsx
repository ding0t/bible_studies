// Bundle entry for the scripture-link explorer, mounted into docs/content/references.md.
// scripture-links.json is generated from bible-text.db by references/build/export_links.py and
// COMMITTED -- bible-text.db is a gitignored build artifact, so CI cannot regenerate it. Re-run
// that script by hand when the link data changes.
import { createRoot } from 'react-dom/client';
import data from '../../../docs/data/scripture-links.json' with { type: 'json' };
import ErrorBoundary from '../components/ErrorBoundary';
import ScriptureLinks from '../components/ScriptureLinks';

const container = document.getElementById('references-root');

if (container) {
  createRoot(container).render(
    <ErrorBoundary componentName="Scripture Links">
      <ScriptureLinks data={data} />
    </ErrorBoundary>
  );
}
