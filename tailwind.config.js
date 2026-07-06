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
        deepl: {
          blue: '#0F2B5B',
          lightBlue: '#1F4690',
          bg: '#F7F8FA',
          border: '#E4E7ED',
          text: '#1A2233',
          textSecondary: '#6B7280',
        }
      }
    },
  },
  plugins: [],
}
