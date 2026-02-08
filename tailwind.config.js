/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./autotradespot/templates/**/*.{html,js}',
    './autotradespot/static/front-end/**/*.{jsx}',
  ],
  safelist: [
    'alert-success',
    'alert-info',
    'alert-warning',
    'alert-error',
    'textarea',
    'textarea-bordered',
    'select',
    'select-bordered',
    'select-sm',
    'step-primary',
    'step-success',
    'step-warning',
  ],
  theme: {
    extend: {
      boxShadow: {
        'inner-fade':
          'inset 0px -50px -100px 50px, inset 0px 50px 100px -50px;',
      },
      colors: {
        base: {
          light: '#67e8f9',
          DEFAULT: '#06b6d4',
          dark: '#0e7490',
        },
        'white-text': {
          light: '#67e8f9',
          DEFAULT: '#f9f8eb',
          dark: '#0e7490',
        },
        'icon-green': {
          light: '#97c5b4',
          DEFAULT: '#76b39d',
          dark: '#589e85',
        },
        'high-contrast': {
          light: '#496085',
          DEFAULT: '#496085',
          dark: '#374864',
        },
      },
    },
    plugins: [],
  },
  variants: {
    extend: {
      textColor: ['disabled'],
      cursor: ['disabled'],
      transform: ['checked'],
    },
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: ['light', 'dark'],
  },
};
