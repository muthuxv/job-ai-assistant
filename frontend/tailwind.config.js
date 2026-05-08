/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        space: {
          950: '#0a0a0f',
          900: '#12121a',
          800: '#1a1a2e',
        },
        neon: {
          violet: '#a855f7',
          cyan: '#06b6d4',
          pink: '#ec4899',
          purple: '#8b5cf6',
        },
      },
      boxShadow: {
        'neon-violet': '0 0 20px rgba(168, 85, 247, 0.5)',
        'neon-cyan': '0 0 20px rgba(6, 182, 212, 0.5)',
        'neon-pink': '0 0 20px rgba(236, 72, 153, 0.5)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      backdropBlur: {
        'xs': '2px',
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          'from': { boxShadow: '0 0 10px rgba(168, 85, 247, 0.5)' },
          'to': { boxShadow: '0 0 20px rgba(168, 85, 247, 0.8)' },
        }
      }
    },
  },
  plugins: [],
}
