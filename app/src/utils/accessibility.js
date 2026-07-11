/**
 * Accessibility utilities for keyboard navigation and ARIA support
 */

/**
 * Handle keyboard navigation for list items
 * @param {KeyboardEvent} event - The keyboard event
 * @param {Object} options - Navigation options
 * @param {Function} options.onSelect - Called when Enter/Space is pressed
 * @param {Function} options.onNext - Called when ArrowDown/ArrowRight is pressed
 * @param {Function} options.onPrev - Called when ArrowUp/ArrowLeft is pressed
 * @param {Function} options.onFirst - Called when Home is pressed
 * @param {Function} options.onLast - Called when End is pressed
 */
export const handleListKeyDown = (event, { onSelect, onNext, onPrev, onFirst, onLast }) => {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault();
      onSelect?.();
      break;
    case 'ArrowDown':
    case 'ArrowRight':
      event.preventDefault();
      onNext?.();
      break;
    case 'ArrowUp':
    case 'ArrowLeft':
      event.preventDefault();
      onPrev?.();
      break;
    case 'Home':
      event.preventDefault();
      onFirst?.();
      break;
    case 'End':
      event.preventDefault();
      onLast?.();
      break;
    default:
      break;
  }
};

/**
 * Generate unique IDs for ARIA relationships
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
let idCounter = 0;
export const generateId = (prefix = 'aria') => {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
};

/**
 * Screen reader only styles (visually hidden but accessible)
 */
export const srOnly = {
  position: 'absolute',
  width: '1px',
  height: '1px',
  padding: 0,
  margin: '-1px',
  overflow: 'hidden',
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap',
  border: 0,
};

/**
 * Focus visible styles for keyboard navigation
 * @param {Object} colors - Color constants
 * @returns {Object} CSS styles object
 */
export const focusVisible = (colors) => ({
  outline: `2px solid ${colors.blue[500]}`,
  outlineOffset: '2px',
});

/**
 * Announce message to screen readers using live region
 * @param {string} message - Message to announce
 * @param {string} priority - 'polite' or 'assertive'
 */
export const announceToScreenReader = (message, priority = 'polite') => {
  const announcer = document.getElementById('sr-announcer') || createAnnouncer();
  announcer.setAttribute('aria-live', priority);
  announcer.textContent = message;

  // Clear after announcement
  setTimeout(() => {
    announcer.textContent = '';
  }, 1000);
};

const createAnnouncer = () => {
  const announcer = document.createElement('div');
  announcer.id = 'sr-announcer';
  Object.assign(announcer.style, srOnly);
  announcer.setAttribute('aria-live', 'polite');
  announcer.setAttribute('aria-atomic', 'true');
  document.body.appendChild(announcer);
  return announcer;
};
