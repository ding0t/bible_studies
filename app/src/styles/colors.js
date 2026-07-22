/**
 * Centralized color constants for the Bible Studies application.
 * Colors follow Tailwind CSS naming conventions for familiarity.
 */

export const colors = {
  // Primary Blues
  blue: {
    50: '#dbeafe',
    100: '#bfdbfe',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    light: '#f0f9ff',
  },

  // Indigo (selection/focus states)
  indigo: {
    50: '#eef2ff',
    100: '#e0e7ff',
    600: '#4f46e5',
    light: '#f0f4ff',
  },

  // Slates (text, backgrounds)
  slate: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    900: '#1e293b',
  },

  // Grays (borders, subtle elements)
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#666666',
    light: '#999999',
  },

  // Semantic accent colors
  accent: {
    red: '#dc2626',
    yellow: '#fbbf24',
    amber: '#fef3c7',
  },

  // Base colors
  white: '#ffffff',
  transparent: 'transparent',

  // Overlay colors
  overlay: {
    dark: 'rgba(0, 0, 0, 0.5)',
    darkLight: 'rgba(0, 0, 0, 0.3)',
    darkSubtle: 'rgba(0, 0, 0, 0.1)',
    light: 'rgba(255, 255, 255, 0.1)',
    lightHover: 'rgba(255, 255, 255, 0.15)',
    lightMedium: 'rgba(255, 255, 255, 0.2)',
    lightStrong: 'rgba(255, 255, 255, 0.3)',
  },
};

// Semantic aliases for common use cases
export const text = {
  primary: colors.slate[900],
  secondary: colors.slate[600],
  muted: colors.slate[400],
  link: colors.blue[600],
  linkHover: colors.blue[700],
};

export const background = {
  page: colors.slate[50],
  card: colors.gray[100],
  section: colors.gray[50],
  modal: colors.slate[900],
};

export const border = {
  light: colors.gray[200],
  default: colors.gray[300],
  focus: colors.indigo[600],
};

export const button = {
  primary: colors.blue[500],
  primaryHover: colors.blue[800],
  primaryText: colors.blue[800],
  background: colors.blue[50],
  backgroundHover: colors.blue[100],
};
