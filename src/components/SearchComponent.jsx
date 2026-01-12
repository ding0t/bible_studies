import React, { useState, useEffect } from 'react';
import { X, Search as SearchIcon } from 'lucide-react';

export default function SearchComponent() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [pagefindIndex, setPagefindIndex] = useState(null);

  // Load Pagefind index
  useEffect(() => {
    const loadPagefind = async () => {
      try {
        // @ts-ignore
        if (window.pagefind) {
          // @ts-ignore
          const pf = await window.pagefind.init();
          setPagefindIndex(pf);
        }
      } catch (e) {
        console.error('Failed to load Pagefind:', e);
      }
    };

    if (isOpen) {
      // Load the Pagefind script if not already loaded
      if (!document.querySelector('script[src*="pagefind"]')) {
        const script = document.createElement('script');
        script.src = '/pagefind/pagefind.js';
        script.async = true;
        script.onload = loadPagefind;
        document.head.appendChild(script);
      } else {
        loadPagefind();
      }
    }
  }, [isOpen]);

  // Handle search
  useEffect(() => {
    const search = async () => {
      if (!query.trim()) {
        setResults([]);
        return;
      }

      setIsSearching(true);
      try {
        if (pagefindIndex) {
          // @ts-ignore
          const searchResults = await pagefindIndex.search(query);
          
          // Get more details about each result
          const detailedResults = await Promise.all(
            searchResults.results.slice(0, 10).map(async (result) => {
              // @ts-ignore
              const data = await result.data();
              return {
                id: result.id,
                title: data.meta.title,
                excerpt: data.excerpt,
                url: data.url,
              };
            })
          );
          
          setResults(detailedResults);
        }
      } catch (e) {
        console.error('Search error:', e);
      } finally {
        setIsSearching(false);
      }
    };

    const debounceTimer = setTimeout(() => {
      if (pagefindIndex) {
        search();
      }
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [query, pagefindIndex]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeydown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(!isOpen);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  }, [isOpen]);

  return (
    <>
      {/* Search Button in Header */}
      <button
        onClick={() => setIsOpen(true)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.5rem 1rem',
          background: 'rgba(255, 255, 255, 0.1)',
          color: '#cbd5e1',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '0.375rem',
          cursor: 'pointer',
          fontSize: '0.875rem',
          transition: 'all 0.2s',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        }}
      >
        <SearchIcon size={16} />
        <span>Search</span>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', opacity: 0.7 }}>
          ⌘K
        </span>
      </button>

      {/* Search Modal */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1000,
            display: 'flex',
            justifyContent: 'center',
            paddingTop: '5rem',
          }}
          onClick={() => setIsOpen(false)}
        >
          <div
            style={{
              width: '90%',
              maxWidth: '600px',
              background: '#1e293b',
              borderRadius: '0.5rem',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Search Input */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '1rem',
                borderBottom: '1px solid #334155',
              }}
            >
              <SearchIcon size={20} color="#94a3b8" />
              <input
                type="text"
                placeholder="Search studies, scriptures, topics..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoFocus
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  color: '#f1f5f9',
                  fontSize: '1rem',
                  outline: 'none',
                }}
              />
              <button
                onClick={() => setIsOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#94a3b8',
                  cursor: 'pointer',
                  padding: '0.25rem',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Search Results */}
            <div
              style={{
                maxHeight: '400px',
                overflowY: 'auto',
                padding: '0.5rem',
              }}
            >
              {isSearching ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                  Searching...
                </div>
              ) : query.trim() === '' ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                  <p>Start typing to search</p>
                  <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                    Search through studies, scriptures, and topics
                  </p>
                </div>
              ) : results.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                  No results found for "{query}"
                </div>
              ) : (
                results.map((result) => (
                  <a
                    key={result.id}
                    href={result.url}
                    onClick={() => setIsOpen(false)}
                    style={{
                      display: 'block',
                      padding: '1rem',
                      margin: '0.25rem',
                      borderRadius: '0.375rem',
                      background: '#334155',
                      color: '#f1f5f9',
                      textDecoration: 'none',
                      transition: 'all 0.2s',
                      cursor: 'pointer',
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.background = '#475569';
                      e.currentTarget.style.transform = 'translateX(4px)';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.background = '#334155';
                      e.currentTarget.style.transform = 'translateX(0)';
                    }}
                  >
                    <h4
                      style={{
                        color: '#fbbf24',
                        fontSize: '0.95rem',
                        marginBottom: '0.25rem',
                        fontWeight: '600',
                      }}
                    >
                      {result.title}
                    </h4>
                    <p
                      style={{
                        color: '#cbd5e1',
                        fontSize: '0.85rem',
                        lineHeight: '1.4',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                      dangerouslySetInnerHTML={{ __html: result.excerpt }}
                    />
                  </a>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
