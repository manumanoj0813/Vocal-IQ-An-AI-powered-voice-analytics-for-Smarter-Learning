import React, { createContext, useContext, useEffect, useState } from 'react';
import { useColorMode } from '@chakra-ui/react';

interface ThemeContextType {
  colorMode: string;
  toggleColorMode: () => void;
  setColorMode: (mode: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { colorMode, setColorMode: setChakraColorMode } = useColorMode();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Load saved theme preference from localStorage
    const savedTheme = localStorage.getItem('vocal-iq-theme');
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      setChakraColorMode(savedTheme);
    }
    setIsInitialized(true);
  }, [setChakraColorMode]);

  const setColorMode = (mode: 'light' | 'dark') => {
    setChakraColorMode(mode);
    localStorage.setItem('vocal-iq-theme', mode);
  };

  const handleToggleColorMode = () => {
    const newMode = colorMode === 'light' ? 'dark' : 'light';
    setColorMode(newMode);
  };

  if (!isInitialized) {
    return null; // or a loading spinner
  }

  return (
    <ThemeContext.Provider
      value={{
        colorMode,
        toggleColorMode: handleToggleColorMode,
        setColorMode,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}; 