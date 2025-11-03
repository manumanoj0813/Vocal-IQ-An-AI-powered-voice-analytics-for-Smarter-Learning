import React from 'react';
import { IconButton, useColorModeValue, Tooltip } from '@chakra-ui/react';
import { FaSun, FaMoon } from 'react-icons/fa';
import { useTheme } from '../contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { colorMode, toggleColorMode } = useTheme();
  const isDark = colorMode === 'dark';
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  return (
    <Tooltip 
      label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      placement="bottom"
    >
      <IconButton
        aria-label="Toggle theme"
        icon={isDark ? <FaSun /> : <FaMoon />}
        onClick={toggleColorMode}
        variant="outline"
        size="md"
        bg={bgColor}
        borderColor={borderColor}
        color={useColorModeValue('gray.600', 'gray.300')}
        _hover={{
          bg: hoverBg,
          borderColor: useColorModeValue('purple.300', 'purple.400'),
          color: useColorModeValue('purple.600', 'purple.400'),
        }}
        _active={{
          bg: hoverBg,
        }}
      />
    </Tooltip>
  );
}; 