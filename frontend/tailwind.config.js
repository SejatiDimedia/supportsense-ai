/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar: {
          bg: '#0E1116',
          hover: '#181C23',
          card: '#181C23',
          border: 'rgba(255, 255, 255, 0.08)',
          text: '#9CA3AF',
        },
        canvas: {
          bg: '#FFFFFF',
          surface: '#F8F9FA',
          border: '#E5E7EB',
          muted: '#6B7280',
        },
        lime: {
          300: '#E4FA66',
          400: '#D4F638',
          500: '#C6F432',
          hover: '#B5E424',
        },
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
            text: '#10B981',
            border: 'rgba(16, 185, 129, 0.25)',
          },
          kag: {
            bg: 'rgba(139, 92, 246, 0.12)',
            text: '#8B5CF6',
            border: 'rgba(139, 92, 246, 0.25)',
          },
          hybrid: {
            bg: 'rgba(245, 158, 11, 0.12)',
            text: '#F59E0B',
            border: 'rgba(245, 158, 11, 0.25)',
          },
          direct: {
            bg: 'rgba(59, 130, 246, 0.12)',
            text: '#3B82F6',
            border: 'rgba(59, 130, 246, 0.25)',
          },
          escalated: {
            bg: 'rgba(239, 68, 68, 0.12)',
            text: '#EF4444',
            border: 'rgba(239, 68, 68, 0.25)',
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
