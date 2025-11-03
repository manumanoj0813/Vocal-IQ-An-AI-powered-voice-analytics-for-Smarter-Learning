import React from 'react';
import { 
  Box, 
  Text, 
  HStack, 
  VStack, 
  Icon, 
  Progress,
  useColorModeValue,
  Badge,
  Tooltip
} from '@chakra-ui/react';
import { 
  FaMicrophone, 
  FaChartLine, 
  FaTrophy, 
  FaClock,
  FaFire,
  FaStar,
  FaTrendingUp,
  FaTarget
} from 'react-icons/fa';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ElementType;
  color?: string;
  progress?: number;
  trend?: 'up' | 'down' | 'neutral';
  badge?: string;
  tooltip?: string;
  className?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  icon = FaChartLine,
  color = 'purple',
  progress,
  trend,
  badge,
  tooltip,
  className = ''
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return FaTrendingUp;
      case 'down':
        return FaTrendingUp;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'green.500';
      case 'down':
        return 'red.500';
      default:
        return 'gray.500';
    }
  };

  const CardContent = (
    <Box
      bg={bgColor}
      p={6}
      borderRadius="xl"
      border="1px solid"
      borderColor={borderColor}
      boxShadow="0 4px 20px rgba(0,0,0,0.08)"
      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      className={`modern-card ${className}`}
      _hover={{
        transform: 'translateY(-4px)',
        boxShadow: '0 8px 30px rgba(0,0,0,0.12)'
      }}
    >
      <HStack justify="space-between" align="start" mb={4}>
        <VStack align="start" spacing={1}>
          <Text
            fontSize="sm"
            fontWeight="500"
            color={textColor}
            textTransform="uppercase"
            letterSpacing="wide"
          >
            {title}
          </Text>
          <HStack spacing={2} align="baseline">
            <Text
              fontSize="2xl"
              fontWeight="700"
              color="gray.800"
              className="gradient-text-static"
            >
              {value}
            </Text>
            {badge && (
              <Badge
                colorScheme={color}
                variant="subtle"
                fontSize="xs"
                px={2}
                py={1}
                borderRadius="full"
              >
                {badge}
              </Badge>
            )}
          </HStack>
          {subtitle && (
            <Text fontSize="sm" color={textColor} opacity={0.8}>
              {subtitle}
            </Text>
          )}
        </VStack>

        <VStack spacing={2} align="end">
          <Box
            p={3}
            bg={`${color}.50`}
            borderRadius="lg"
            className="pulse"
          >
            <Icon
              as={icon}
              boxSize={6}
              color={`${color}.500`}
            />
          </Box>
          
          {trend && (
            <HStack spacing={1}>
              <Icon
                as={getTrendIcon()}
                boxSize={3}
                color={getTrendColor()}
                transform={trend === 'down' ? 'rotate(180deg)' : 'none'}
              />
              <Text fontSize="xs" color={getTrendColor()} fontWeight="500">
                {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
              </Text>
            </HStack>
          )}
        </VStack>
      </HStack>

      {progress !== undefined && (
        <VStack spacing={2} align="stretch">
          <HStack justify="space-between">
            <Text fontSize="xs" color={textColor}>
              Progress
            </Text>
            <Text fontSize="xs" fontWeight="500" color={`${color}.500`}>
              {progress}%
            </Text>
          </HStack>
          <Progress
            value={progress}
            colorScheme={color}
            size="sm"
            borderRadius="full"
            bg="gray.100"
            className="fade-in-up"
          />
        </VStack>
      )}
    </Box>
  );

  if (tooltip) {
    return (
      <Tooltip
        label={tooltip}
        placement="top"
        hasArrow
        bg="gray.800"
        color="white"
        borderRadius="lg"
        px={3}
        py={2}
      >
        {CardContent}
      </Tooltip>
    );
  }

  return CardContent;
};

export default StatsCard;
