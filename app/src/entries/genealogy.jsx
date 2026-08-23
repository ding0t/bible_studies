// Bundle entry for the genealogy viewer as it is served today: a mkdocs page, not an Astro page.
// mkdocs owns the page shell (header, sidebar, search, palette toggle); this mounts only the tool
// into a div that docs/content/genealogy.md provides.
import { createRoot } from 'react-dom/client';
import ErrorBoundary from '../components/ErrorBoundary';
import GenealogyViewer from '../components/GenealogyViewer';

const container = document.getElementById('genealogy-root');

// The bundle is loaded from a <script type="module"> on one page only, but a stray load elsewhere
// should do nothing rather than throw into the console.
if (container) {
  createRoot(container).render(
    <ErrorBoundary componentName="Genealogy Viewer">
      <GenealogyViewer />
    </ErrorBoundary>
  );
}
