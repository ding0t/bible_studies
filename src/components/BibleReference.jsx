import React from 'react';
import { parseReference, generateBibleLink, getSiteDisplayName } from '../utils/bibleReference';

/**
 * BibleReference Component
 * Renders a clickable Bible reference that links to external scripture sources
 * 
 * @param {string} text - Raw reference text (e.g., "Genesis 1:27")
 * @param {string} version - Bible version (default: 'esv')
 * @param {string} site - Target site (default: 'blueletterbible')
 */
export const BibleReference = ({ 
  text, 
  version = 'esv', 
  site = 'blueletterbible'
}) => {
  const parsed = parseReference(text);
  
  // If parsing fails, just display raw text
  if (!parsed) {
    return <span style={{ color: '#666' }}>{text}</span>;
  }
  
  const link = generateBibleLink(parsed, version, site);
  const siteName = getSiteDisplayName(site);
  
  return (
    <a
      href={link}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        color: '#2563eb',
        textDecoration: 'underline',
        cursor: 'pointer',
        fontWeight: '500',
        transition: 'color 0.2s'
      }}
      title={`${text} (${version.toUpperCase()}) on ${siteName}`}
      onMouseEnter={(e) => e.target.style.color = '#1d4ed8'}
      onMouseLeave={(e) => e.target.style.color = '#2563eb'}
    >
      {text}
    </a>
  );
};
