// Bundle entry for the prophetic timeline, mounted into docs/content/timeline.md, and for the
// printable History Chart in docs/content/chronology/history-chart.md, which shares its data.
// events.json is generated from study frontmatter by scripts/build-events.js, which build:tools
// runs first -- see package.json.
import { createRoot } from 'react-dom/client';
import events from '../../../docs/data/events.json' with { type: 'json' };
import ErrorBoundary from '../components/ErrorBoundary';
import ChronologyExplorer from '../components/chronology/ChronologyExplorer';
import HistoryChart from '../components/chronology/HistoryChart';

const container = document.getElementById('timeline-root');

if (container) {
  createRoot(container).render(
    <ErrorBoundary componentName="Prophetic Timeline">
      <ChronologyExplorer events={events} />
    </ErrorBoundary>
  );
}

const chartContainer = document.getElementById('history-chart-root');

if (chartContainer) {
  createRoot(chartContainer).render(
    <ErrorBoundary componentName="History Chart">
      <HistoryChart />
    </ErrorBoundary>
  );
}
