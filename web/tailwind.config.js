/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#5E6AD2', // Linear App primary blue
        'secondary': '#8A8F98', // Linear App secondary gray
        'background': '#17181A', // Linear App dark background
        'surface': '#232427', // Linear App surface color
        'success': '#4CB782', // Linear App success green
        'error': '#E5484D', // Linear App error red
        'warning': '#F2BD24', // Linear App warning yellow
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 