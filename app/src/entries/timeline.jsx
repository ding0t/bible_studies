// Bundle entry for the prophetic timeline, mounted into docs/content/timeline.md.
// events.json is generated from study frontmatter by scripts/build-events.js, which build:tools
// runs first -- see package.json.
import { createRoot } from 'react-dom/client';
import events from '../../../docs/data/events.json' with { type: 'json' };
import ErrorBoundary from '../components/ErrorBoundary';
import MillennialWeek from '../components/MillennialWeek';

const container = document.getElementById('timeline-root');

if (container) {
  createRoot(container).render(
    <ErrorBoundary componentName="Prophetic Timeline">
      <MillennialWeek events={events} />
    </ErrorBoundary>
  );
}
