/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        cream: { 50: '#fdfaf6', 100: '#f9f3eb', 200: '#f0e6d6', 300: '#e4d4bc' },
        sand: { 400: '#c4a882', 500: '#b0936a', 600: '#9a7d54' },
        sage: { 400: '#8ba888', 500: '#6b8a68', 600: '#567354' },
        terracotta: { 400: '#c89580', 500: '#b07a62', 600: '#966248' },
        warm: {
          50: '#fdfaf6', 100: '#f7f1e8', 200: '#ebe0d1', 300: '#d4c4ad',
          400: '#a89a82', 500: '#7a6e58', 600: '#5c5341', 700: '#423b2e',
          800: '#2d2820', 900: '#1a1814',
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
