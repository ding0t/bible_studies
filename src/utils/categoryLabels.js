/**
 * Category labels and colors for study organization
 * Shared between studies index and detail pages
 */

export const categoryLabels = {
  'prophecy': { label: '📜 Prophecy Fulfilled in Jesus', color: '#dc2626' },
  'theology': { label: '📖 Theological Studies', color: '#7c3aed' },
  'spiritual-disciplines': { label: '🙏 Spiritual Disciplines', color: '#2563eb' },
  'spiritual discipline': { label: '🙏 Spiritual Disciplines', color: '#2563eb' },
  'sins': { label: '⚠️ Sin & Redemption', color: '#f59e0b' },
  'feasts': { label: '🎉 Feasts & Seasons', color: '#10b981' },
  'sermons': { label: '🎤 Sermons', color: '#06b6d4' },
  'hebrew-studies': { label: '🕎 Hebrew Studies', color: '#8b5cf6' },
  'dreams-visions': { label: '💭 Dreams & Visions', color: '#ec4899' },
  'dreams': { label: '💭 Dreams', color: '#ec4899' },
  'teaching-resources': { label: '📚 Teaching Resources', color: '#0ea5e9' },
  'deliverance': { label: '⛓️ Deliverance & Freedom', color: '#64748b' },
  'investigation': { label: '🔍 Investigation', color: '#78716c' },
  'archeology': { label: '🏺 Archeology', color: '#a16207' },
  'commentaries': { label: '📖 Bible Commentaries', color: '#f59e0b' },
  'other': { label: '📝 Other Studies', color: '#6366f1' }
};

/**
 * Get category info with fallback for unknown categories
 * @param {string} category - Category key
 * @returns {{ label: string, color: string }}
 */
export const getCategoryInfo = (category) => {
  const cat = category || 'other';
  if (categoryLabels[cat]) {
    return categoryLabels[cat];
  }
  // Generate label from category name (capitalize and format)
  const formatted = cat.split('-').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
  return {
    label: `📚 ${formatted}`,
    color: '#6366f1'
  };
};
