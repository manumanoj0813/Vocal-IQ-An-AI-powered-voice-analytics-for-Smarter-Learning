import React from 'react';
import { Box, Spinner, Text, VStack, HStack, Icon } from '@chakra-ui/react';
import { FaBrain, FaMicrophone, FaChartLine } from 'react-icons/fa';

interface LoadingSpinnerProps {
  message?: string;
  type?: 'analysis' | 'recording' | 'processing';
  size?: 'sm' | 'md' | 'lg';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Processing...", 
  type = 'analysis',
  size = 'md'
}) => {
  const getIcon = () => {
    switch (type) {
      case 'recording':
        return FaMicrophone;
      case 'processing':
        return FaChartLine;
      default:
        return FaBrain;
    }
  };

  const getColor = () => {
    switch (type) {
      case 'recording':
        return 'red.500';
      case 'processing':
        return 'blue.500';
      default:
        return 'purple.500';
    }
  };

  const getSize = () => {
    switch (size) {
      case 'sm':
        return { spinner: 'sm', icon: 4, text: 'sm' };
      case 'lg':
        return { spinner: 'xl', icon: 8, text: 'lg' };
      default:
        return { spinner: 'md', icon: 6, text: 'md' };
    }
  };

  const sizes = getSize();

  return (
    <VStack spacing={4} py={8}>
      <Box position="relative">
        <Spinner
          thickness="4px"
          speed="0.8s"
          emptyColor="gray.200"
          color={getColor()}
          size={sizes.spinner}
        />
        <Icon
          as={getIcon()}
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
          boxSize={sizes.icon}
          color={getColor()}
          className="pulse"
        />
      </Box>
      <Text 
        fontSize={sizes.text} 
        color="gray.600" 
        fontWeight="500"
        textAlign="center"
        className="fade-in-up"
      >
        {message}
      </Text>
      <HStack spacing={1} className="fade-in-up" style={{ animationDelay: '0.2s' }}>
        <Box w="2" h="2" bg={getColor()} borderRadius="full" className="pulse" />
        <Box w="2" h="2" bg={getColor()} borderRadius="full" className="pulse" style={{ animationDelay: '0.2s' }} />
        <Box w="2" h="2" bg={getColor()} borderRadius="full" className="pulse" style={{ animationDelay: '0.4s' }} />
      </HStack>
    </VStack>
  );
};

export default LoadingSpinner;
