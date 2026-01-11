/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-app': '#0f0f0f',
        'bg-panel': '#161616',
        'bg-element': '#1e1e1e',
        'bg-hover': '#2a2a2a',
        'border-subtle': '#262626',
        'border-focus': '#404040',
        'text-main': '#e0e0e0',
        'text-muted': '#808080',
        'accent-primary': '#d97757',
        'accent-glow': 'rgba(217, 119, 87, 0.15)',
        'success': '#69b38a',
        'warning': '#e0c285',
        'error': '#e06c75',
      },
      fontFamily: {
        'ui': ['Inter', '-apple-system', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
