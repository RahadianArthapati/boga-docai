/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6c5ce7',
        secondary: '#a29bfe',
        light: '#f9f9f9',
        dark: '#333333',
      },
      borderRadius: {
        'chat': '0.8rem',
      },
    },
  },
  plugins: [],
} 