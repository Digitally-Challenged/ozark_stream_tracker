/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          main: '#1976d2',
          light: '#42a5f5',
          dark: '#1565c0',
          contrastText: '#fff',
        },
        secondary: {
          main: '#9c27b0',
          light: '#ba68c8',
          dark: '#7b1fa2',
          contrastText: '#fff',
        },
        error: {
          main: '#d32f2f',
          light: '#ef5350',
          dark: '#c62828',
          contrastText: '#fff',
        },
        warning: {
          main: '#ed6c02',
          light: '#ff9800',
          dark: '#e65100',
          contrastText: '#fff',
        },
        info: {
          main: '#0288d1',
          light: '#03a9f4',
          dark: '#01579b',
          contrastText: '#fff',
        },
        success: {
          main: '#2e7d32',
          light: '#4caf50',
          dark: '#1b5e20',
          contrastText: '#fff',
        },
        grey: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#eeeeee',
          300: '#e0e0e0',
          400: '#bdbdbd',
          500: '#9e9e9e',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121',
        },
      },
      spacing: {
        // Material UI's spacing units (1 unit = 8px)
        0.5: '4px',
        1: '8px',
        2: '16px',
        3: '24px',
        4: '32px',
        5: '40px',
        6: '48px',
        7: '56px',
        8: '64px',
      },
      borderRadius: {
        // Material UI's default border radius values
        none: '0',
        sm: '4px',
        DEFAULT: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
        '2xl': '16px',
      },
      fontFamily: {
        // Material UI's default font family
        sans: ['Roboto', 'Arial', 'sans-serif'],
      },
      fontSize: {
        // Material UI's typography scale
        xs: ['0.75rem', { lineHeight: '1.66' }],
        sm: ['0.875rem', { lineHeight: '1.43' }],
        base: ['1rem', { lineHeight: '1.5' }],
        lg: ['1.125rem', { lineHeight: '1.5' }],
        xl: ['1.25rem', { lineHeight: '1.334' }],
        '2xl': ['1.5rem', { lineHeight: '1.334' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
        '4xl': ['2.25rem', { lineHeight: '1.167' }],
        '5xl': ['3rem', { lineHeight: '1.167' }],
      },
      boxShadow: {
        // Material UI's elevation levels
        1: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        2: '0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)',
        3: '0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)',
        4: '0 15px 25px rgba(0,0,0,0.15), 0 5px 10px rgba(0,0,0,0.05)',
        5: '0 20px 40px rgba(0,0,0,0.2)',
      },
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')],
};
