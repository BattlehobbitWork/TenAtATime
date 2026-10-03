/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Deep purple backgrounds
        plum: {
          50: '#1a1525',
          100: '#221a33',
          200: '#2a2040',
          300: '#33284d',
        },
        // Mid purple for cards/surfaces
        violet: {
          400: '#6b4d8f',
          500: '#5a3d7a',
          600: '#4a2d65',
        },
        // Green/teal accents (replaces sage)
        teal: {
          400: '#4db8a4',
          500: '#3a9b88',
          600: '#2d7d6f',
        },
        // Soft accent for due/overdue items (replaces terracotta)
        coral: {
          400: '#d97a8c',
          500: '#c45a72',
          600: '#a8455c',
        },
        // Text colors
        ink: {
          50: '#e8e0f0',
          100: '#d4c8e0',
          200: '#b8a8cc',
          300: '#9c8cb5',
          400: '#7a6a98',
          500: '#5e527e',
          600: '#483d62',
          700: '#362d4a',
          800: '#241d33',
          900: '#1a1525',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}
