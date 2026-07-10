import React from 'react';
import { colors } from '../styles/colors';

/**
 * Error Boundary Component
 * Catches JavaScript errors in child component tree and displays fallback UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const { fallback, componentName = 'Component' } = this.props;

      if (fallback) {
        return fallback;
      }

      return (
        <div
          role="alert"
          style={{
            padding: '1.5rem',
            margin: '1rem 0',
            backgroundColor: colors.accent.amber,
            border: `2px solid ${colors.accent.red}`,
            borderRadius: '0.5rem',
            fontFamily: 'system-ui, sans-serif',
          }}
        >
          <h3 style={{ margin: '0 0 0.5rem 0', color: colors.accent.red }}>
            {componentName} failed to load
          </h3>
          <p style={{ margin: '0 0 1rem 0', color: colors.slate[700] }}>
            Something went wrong while displaying this content. Please try refreshing the page.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: colors.blue[500],
              color: colors.white,
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer',
              fontWeight: '500',
            }}
          >
            Refresh Page
          </button>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ marginTop: '1rem' }}>
              <summary style={{ cursor: 'pointer', color: colors.slate[600] }}>
                Error Details (Development Only)
              </summary>
              <pre
                style={{
                  marginTop: '0.5rem',
                  padding: '0.75rem',
                  backgroundColor: colors.slate[900],
                  color: colors.slate[100],
                  borderRadius: '0.25rem',
                  overflow: 'auto',
                  fontSize: '0.75rem',
                }}
              >
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
