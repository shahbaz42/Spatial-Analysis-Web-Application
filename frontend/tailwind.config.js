/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef6ee',
          100: '#fdecd7',
          200: '#fbd5ae',
          300: '#f7b77a',
          400: '#f39044',
          500: '#f0711f',
          600: '#e15715',
          700: '#bb4113',
          800: '#953518',
          900: '#782e16',
          950: '#40150a',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
