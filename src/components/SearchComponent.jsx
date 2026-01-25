import React, { useState, useEffect, useRef } from 'react';
import { X, Search as SearchIcon } from 'lucide-react';
import { colors } from '../styles/colors';

export default function SearchComponent() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [pagefindIndex, setPagefindIndex] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const resultsRef = useRef(null);

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

  // Handle keyboard navigation in results
  const handleInputKeyDown = (e) => {
    if (results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, -1));
        break;
      case 'Enter':
        if (selectedIndex >= 0 && results[selectedIndex]) {
          window.location.href = results[selectedIndex].url;
          setIsOpen(false);
        }
        break;
      default:
        break;
    }
  };

  // Reset selection when results change
  useEffect(() => {
    setSelectedIndex(-1);
  }, [results]);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  return (
    <>
      {/* Search Button in Header */}
      <button
        onClick={() => setIsOpen(true)}
        aria-label="Search studies (Ctrl+K)"
        aria-haspopup="dialog"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.5rem 1rem',
          background: colors.overlay.light,
          color: colors.slate[300],
          border: `1px solid ${colors.overlay.lightMedium}`,
          borderRadius: '0.375rem',
          cursor: 'pointer',
          fontSize: '0.875rem',
          transition: 'all 0.2s',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = colors.overlay.lightHover;
          e.currentTarget.style.borderColor = colors.overlay.lightStrong;
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = colors.overlay.light;
          e.currentTarget.style.borderColor = colors.overlay.lightMedium;
        }}
      >
        <SearchIcon size={16} aria-hidden="true" />
        <span>Search</span>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', opacity: 0.7 }} aria-hidden="true">
          ⌘K
        </span>
      </button>

      {/* Search Modal */}
      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Search dialog"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: colors.overlay.dark,
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
              maxHeight: 'calc(100vh - 10rem)',
              background: colors.slate[900],
              borderRadius: '0.5rem',
              boxShadow: `0 20px 25px -5px ${colors.overlay.darkLight}`,
              display: 'flex',
              flexDirection: 'column',
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
                borderBottom: `1px solid ${colors.slate[700]}`,
              }}
            >
              <SearchIcon size={20} color={colors.slate[400]} aria-hidden="true" />
              <input
                ref={inputRef}
                type="search"
                placeholder="Search studies, scriptures, topics..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleInputKeyDown}
                aria-label="Search"
                aria-describedby="search-hint"
                aria-controls="search-results"
                aria-activedescendant={selectedIndex >= 0 ? `result-${selectedIndex}` : undefined}
                autoComplete="off"
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  color: colors.slate[100],
                  fontSize: '1rem',
                  outline: 'none',
                }}
              />
              <button
                onClick={() => setIsOpen(false)}
                aria-label="Close search"
                style={{
                  background: 'none',
                  border: 'none',
                  color: colors.slate[400],
                  cursor: 'pointer',
                  padding: '0.25rem',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <X size={20} aria-hidden="true" />
              </button>
            </div>

            {/* Search Results */}
            <div
              ref={resultsRef}
              id="search-results"
              role="listbox"
              aria-label="Search results"
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '0.5rem',
              }}
            >
              <div id="search-hint" style={{ position: 'absolute', left: '-9999px' }}>
                Use arrow keys to navigate results, Enter to select
              </div>
              {isSearching ? (
                <div role="status" aria-live="polite" style={{ padding: '2rem', textAlign: 'center', color: colors.slate[400] }}>
                  Searching...
                </div>
              ) : query.trim() === '' ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: colors.slate[400] }}>
                  <p>Start typing to search</p>
                  <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                    Search through studies, scriptures, and topics
                  </p>
                </div>
              ) : results.length === 0 ? (
                <div role="status" aria-live="polite" style={{ padding: '2rem', textAlign: 'center', color: colors.slate[400] }}>
                  No results found for "{query}"
                </div>
              ) : (
                <>
                  <div role="status" aria-live="polite" style={{ position: 'absolute', left: '-9999px' }}>
                    {results.length} results found
                  </div>
                  {results.map((result, index) => (
                    <a
                      key={result.id}
                      id={`result-${index}`}
                      href={result.url}
                      role="option"
                      aria-selected={selectedIndex === index}
                      onClick={() => setIsOpen(false)}
                      onMouseEnter={() => setSelectedIndex(index)}
                      style={{
                        display: 'block',
                        padding: '1rem',
                        margin: '0.25rem',
                        borderRadius: '0.375rem',
                        background: selectedIndex === index ? colors.slate[600] : colors.slate[700],
                        color: colors.slate[100],
                        textDecoration: 'none',
                        transition: 'all 0.2s',
                        cursor: 'pointer',
                        outline: selectedIndex === index ? `2px solid ${colors.blue[500]}` : 'none',
                        outlineOffset: '-2px',
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.background = colors.slate[600];
                        e.currentTarget.style.transform = 'translateX(4px)';
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.background = selectedIndex === index ? colors.slate[600] : colors.slate[700];
                        e.currentTarget.style.transform = 'translateX(0)';
                      }}
                    >
                      <h4
                        style={{
                          color: colors.accent.yellow,
                          fontSize: '0.95rem',
                          marginBottom: '0.25rem',
                          fontWeight: '600',
                        }}
                      >
                        {result.title}
                      </h4>
                      <p
                        style={{
                          color: colors.slate[300],
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
                  ))}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
