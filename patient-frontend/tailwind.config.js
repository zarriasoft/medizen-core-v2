/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand': {
          dark: '#1e382d', // Dark green from the image header
          light: '#355c47', // Lighter green
          gold: '#d4af37',  // Gold accent
        }
      }
    },
  },
  plugins: [],
}
