import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Text, 
  HStack, 
  Icon, 
  Button, 
  VStack,
  useColorModeValue,
  SlideFade,
  ScaleFade
} from '@chakra-ui/react';
import { 
  FaCheckCircle, 
  FaExclamationTriangle, 
  FaInfoCircle, 
  FaTimes,
  FaRocket,
  FaStar,
  FaGift
} from 'react-icons/fa';

interface NotificationBannerProps {
  type?: 'success' | 'warning' | 'info' | 'premium';
  title: string;
  message?: string;
  duration?: number;
  onClose?: () => void;
  showCloseButton?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const NotificationBanner: React.FC<NotificationBannerProps> = ({
  type = 'info',
  title,
  message,
  duration = 5000,
  onClose,
  showCloseButton = true,
  action
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isClosing, setIsClosing] = useState(false);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const getIcon = () => {
    switch (type) {
      case 'success':
        return FaCheckCircle;
      case 'warning':
        return FaExclamationTriangle;
      case 'premium':
        return FaStar;
      default:
        return FaInfoCircle;
    }
  };

  const getColor = () => {
    switch (type) {
      case 'success':
        return 'green.500';
      case 'warning':
        return 'orange.500';
      case 'premium':
        return 'purple.500';
      default:
        return 'blue.500';
    }
  };

  const getBgGradient = () => {
    switch (type) {
      case 'success':
        return 'linear(to-r, green.50, green.100)';
      case 'warning':
        return 'linear(to-r, orange.50, orange.100)';
      case 'premium':
        return 'linear(to-r, purple.50, pink.50)';
      default:
        return 'linear(to-r, blue.50, blue.100)';
    }
  };

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, 300);
  };

  if (!isVisible) return null;

  return (
    <SlideFade in={isVisible && !isClosing} offsetY={-20}>
      <Box
        bg={bgColor}
        bgGradient={getBgGradient()}
        border="1px solid"
        borderColor={borderColor}
        borderRadius="xl"
        p={4}
        boxShadow="0 10px 25px rgba(0,0,0,0.1)"
        position="relative"
        overflow="hidden"
        className="modern-card"
      >
        {/* Shimmer effect */}
        <Box
          position="absolute"
          top="0"
          left="-100%"
          w="100%"
          h="100%"
          bg="linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)"
          className="shimmer"
        />
        
        <HStack spacing={4} align="start">
          <Icon
            as={getIcon()}
            boxSize={6}
            color={getColor()}
            className="pulse"
          />
          
          <VStack align="start" spacing={2} flex={1}>
            <Text
              fontSize="lg"
              fontWeight="600"
              color="gray.800"
              className="fade-in-up"
            >
              {title}
            </Text>
            {message && (
              <Text
                fontSize="sm"
                color="gray.600"
                className="fade-in-up"
                style={{ animationDelay: '0.1s' }}
              >
                {message}
              </Text>
            )}
            {action && (
              <Button
                size="sm"
                colorScheme={type === 'premium' ? 'purple' : type}
                variant="solid"
                onClick={action.onClick}
                className="btn-hover"
                mt={2}
              >
                {action.label}
              </Button>
            )}
          </VStack>

          {showCloseButton && (
            <Button
              size="sm"
              variant="ghost"
              onClick={handleClose}
              className="interactive"
              minW="auto"
              p={2}
            >
              <Icon as={FaTimes} boxSize={4} />
            </Button>
          )}
        </HStack>

        {/* Progress bar */}
        {duration > 0 && (
          <Box
            position="absolute"
            bottom="0"
            left="0"
            h="3px"
            bg={getColor()}
            borderRadius="0 0 12px 12px"
            className="loading-shimmer"
            style={{
              animation: `shimmer ${duration}ms linear forwards`,
              width: '100%'
            }}
          />
        )}
      </Box>
    </SlideFade>
  );
};

export default NotificationBanner;
