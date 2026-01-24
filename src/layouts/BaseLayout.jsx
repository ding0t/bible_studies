import React from 'react';

export default function BaseLayout({ children, title = 'Biblical Studies' }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width" />
        <meta name="description" content="Interactive Bible studies and prophetic timeline" />
        <title>{`${title} | Biblical Studies`}</title>
        {/* Mermaid for diagram rendering */}
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
          {`
            if (typeof mermaid !== 'undefined') {
              mermaid.initialize({ startOnLoad: true, theme: 'default' });
              mermaid.contentLoaded();
            }
          `}
        </script>
        <style>{`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
          }

          header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          }

          header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
          }

          header p {
            opacity: 0.9;
            font-size: 0.95rem;
          }

          nav {
            background: white;
            border-bottom: 1px solid #e2e8f0;
            padding: 1rem 2rem;
          }

          nav ul {
            list-style: none;
            display: flex;
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
          }

          nav a {
            text-decoration: none;
            color: #475569;
            font-weight: 500;
            transition: color 0.2s;
          }

          nav a:hover {
            color: #3b82f6;
          }

          main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
          }

          footer {
            background: #1e293b;
            color: white;
            padding: 2rem;
            text-align: center;
            margin-top: 4rem;
            font-size: 0.875rem;
          }

          /* Mermaid diagram styling */
          .mermaid {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #e2e8f0;
            overflow-x: auto;
          }

          .mermaid svg {
            max-width: 100%;
            height: auto;
          }
        `}</style>
      </head>
      <body>
        <header>
          <h1>📖 Biblical Studies</h1>
          <p>Interactive exploration of Scripture and prophecy</p>
        </header>

        <nav>
          <ul>
            <li><a href="/">Timeline</a></li>
            <li><a href="/studies">Studies</a></li>
            <li><a href="/bible">Scripture</a></li>
          </ul>
        </nav>

        <main>
          {children}
        </main>

        <footer>
          <p>&copy; 2026 Biblical Studies by ding0t. Built with Astro.</p>
        </footer>
      </body>
    </html>
  );
}
