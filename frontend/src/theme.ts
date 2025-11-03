import { extendTheme, type ThemeConfig } from '@chakra-ui/react';
const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
};

export const theme = extendTheme({
  config,
  colors: {
    brand: {
      50: '#eef2ff',
      100: '#e0e7ff',
      200: '#c7d2fe',
      300: '#a5b4fc',
      400: '#818cf8',
      500: '#6366f1',
      600: '#4f46e5',
      700: '#4338ca',
      800: '#3730a3',
      900: '#312e81',
    },
    accent: {
      50: '#fdf4ff',
      100: '#fae8ff',
      200: '#f5d0fe',
      300: '#f0abfc',
      400: '#e879f9',
      500: '#d946ef',
      600: '#c026d3',
      700: '#a21caf',
      800: '#86198f',
      900: '#701a75',
    },
    purple: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7c3aed',
      800: '#6b21a8',
      900: '#581c87',
    },
    pink: {
      50: '#fdf2f8',
      100: '#fce7f3',
      200: '#fbcfe8',
      300: '#f9a8d4',
      400: '#f472b6',
      500: '#ec4899',
      600: '#db2777',
      700: '#be185d',
      800: '#9d174d',
      900: '#831843',
    },
    gradient: {
      primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      ocean: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      sunset: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      aurora: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
      cosmic: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)',
      premium: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
      glass: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
      neon: 'linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00f2fe 100%)',
      fire: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 50%, #f06595 100%)',
      emerald: 'linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%)',
    },
  },
  fonts: {
    heading: '"Inter", "Poppins", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
    body: '"Inter", "Poppins", "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif',
  },
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
    '5xl': '3rem',
    '6xl': '3.75rem',
    '7xl': '4.5rem',
    '8xl': '6rem',
    '9xl': '8rem',
  },
  space: {
    px: '1px',
    0.5: '0.125rem',
    1: '0.25rem',
    1.5: '0.375rem',
    2: '0.5rem',
    2.5: '0.625rem',
    3: '0.75rem',
    3.5: '0.875rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    7: '1.75rem',
    8: '2rem',
    9: '2.25rem',
    10: '2.5rem',
    12: '3rem',
    14: '3.5rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
    28: '7rem',
    32: '8rem',
    36: '9rem',
    40: '10rem',
    44: '11rem',
    48: '12rem',
    52: '13rem',
    56: '14rem',
    60: '15rem',
    64: '16rem',
    72: '18rem',
    80: '20rem',
    96: '24rem',
  },
  breakpoints: {
    base: '0em',
    sm: '30em',
    md: '48em',
    lg: '62em',
    xl: '80em',
    '2xl': '96em',
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'semibold',
        borderRadius: 'lg',
        _focus: {
          boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.3)',
        },
      },
      variants: {
        solid: {
          bg: 'gradient.primary',
          color: 'white',
          _hover: {
            bg: 'gradient.secondary',
            transform: 'translateY(-2px)',
            boxShadow: 'lg',
          },
          _active: {
            transform: 'translateY(0)',
          },
        },
        outline: {
          bg: 'transparent',
          color: 'brand.500',
          border: '2px solid',
          borderColor: 'brand.500',
          _hover: {
            bg: 'brand.50',
            borderColor: 'brand.600',
            color: 'brand.600',
          },
        },
      },
      defaultProps: {
        variant: 'solid',
        colorScheme: 'brand',
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: 'white',
          border: '1px solid',
          borderColor: 'gray.200',
          borderRadius: 'xl',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          _hover: {
            transform: 'translateY(-2px)',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          },
          transition: 'all 0.3s ease',
        },
      },
    },
    Progress: {
      baseStyle: {
        track: {
          bg: 'gray.100',
          borderRadius: 'full',
        },
        filledTrack: {
          bg: 'gradient.ocean',
          borderRadius: 'full',
        },
      },
      defaultProps: {
        colorScheme: 'brand',
      },
    },
    Tabs: {
      variants: {
        'soft-rounded': {
          tab: {
            bg: 'gray.50',
            color: 'gray.600',
            fontWeight: 'medium',
            _selected: {
              bg: 'gradient.primary',
              color: 'white',
              boxShadow: 'md',
            },
            _hover: {
              bg: 'gray.100',
            },
          },
        },
      },
    },
  },
  styles: {
    global: (props: any) => ({
      'html, body': {
        scrollBehavior: 'smooth',
      },
      body: {
        bg: props.colorMode === 'dark' ? 'gray.900' : '#f8fafc',
        color: props.colorMode === 'dark' ? 'white' : 'gray.800',
        fontFamily: 'body',
        lineHeight: 'base',
        minHeight: '100vh',
      },
      '*': {
        boxSizing: 'border-box',
      },
      '::selection': {
        bg: 'brand.200',
        color: 'brand.800',
      },
      '::-webkit-scrollbar': {
        width: '8px',
      },
      '::-webkit-scrollbar-track': {
        bg: 'gray.100',
        borderRadius: '4px',
      },
      '::-webkit-scrollbar-thumb': {
        bg: 'brand.300',
        borderRadius: '4px',
        '&:hover': {
          bg: 'brand.400',
        },
      },
    }),
  },
}); 