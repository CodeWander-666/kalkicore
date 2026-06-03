/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        gold: { 400: '#D4AF37', 500: '#C5A028', 600: '#B08D2B' },
        cyan: { 400: '#06B6D4', 500: '#0891B2', 600: '#0E7490' },
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'gradient-x': 'gradient-x 3s ease infinite',
        'border-pulse': 'borderPulse 1.2s ease-in-out infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        borderPulse: {
          '0%, 100%': { borderColor: '#ff00cc', boxShadow: '0 0 5px #ff00cc' },
          '25%': { borderColor: '#00ffcc', boxShadow: '0 0 10px #00ffcc' },
          '50%': { borderColor: '#ffcc00', boxShadow: '0 0 15px #ffcc00' },
          '75%': { borderColor: '#00ccff', boxShadow: '0 0 10px #00ccff' },
        },
      },
    },
  },
  plugins: [],
};
