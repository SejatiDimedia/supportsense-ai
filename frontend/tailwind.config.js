/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: '#070A0F',
          900: '#0B0F17',
          850: '#111722',
          800: '#161F2E',
          700: '#232F42',
          600: '#334155',
        },
        route: {
          rag: {
            bg: 'rgba(16, 185, 129, 0.12)',
            text: '#34D399',
            border: 'rgba(52, 211, 153, 0.3)',
          },
          kag: {
            bg: 'rgba(139, 92, 246, 0.12)',
            text: '#A78BFA',
            border: 'rgba(167, 139, 250, 0.3)',
          },
          hybrid: {
            bg: 'rgba(245, 158, 11, 0.12)',
            text: '#FBBF24',
            border: 'rgba(251, 191, 36, 0.3)',
          },
          direct: {
            bg: 'rgba(59, 130, 246, 0.12)',
            text: '#60A5FA',
            border: 'rgba(96, 165, 250, 0.3)',
          },
          escalated: {
            bg: 'rgba(239, 68, 68, 0.14)',
            text: '#F87171',
            border: 'rgba(248, 113, 113, 0.35)',
          }
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
