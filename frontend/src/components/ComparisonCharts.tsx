import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  SimpleGrid,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
} from '@chakra-ui/react';
import { FaChartLine, FaLanguage, FaDownload } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export const ComparisonCharts: React.FC = () => {
  const [comparisonChart, setComparisonChart] = useState<string | null>(null);
  const [languageChart, setLanguageChart] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { getAccessToken, isAuthenticated, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const fetchWithAuth = useCallback(async (url: string, options: RequestInit = {}) => {
    const token = await getAccessToken();
    
    if (!token) {
      logout();
      navigate('/login');
      throw new Error('No authentication token available');
    }
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (response.status === 401) {
      // If we get a 401 after trying with a fresh token, the token is invalid
      logout();
      navigate('/login');
      throw new Error('Session expired. Please log in again.');
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Request failed');
    }
    
    return response;
  }, [getAccessToken, logout, navigate]);
  
  const fetchChart = useCallback(async (endpoint: string, setChart: (data: string) => void) => {
    try {
      const response = await fetchWithAuth(`http://localhost:8000${endpoint}`);
      const text = await response.text();
      setChart(text);
    } catch (error) {
      console.error(`Error fetching chart:`, error);
      throw error;
    }
  }, [fetchWithAuth]);
  
  const loadCharts = useCallback(async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Load comparison chart
      await fetchChart('/comparison-charts', setComparisonChart);
      
      // Load language chart
      await fetchChart('/language-charts', setLanguageChart);
      
      toast({
        title: 'Charts Loaded',
        description: 'Comparison and language charts loaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load charts';
      setError(errorMessage);
      
      // Don't show error toast if user was redirected to login
      if (!errorMessage.includes('Session expired') && !errorMessage.includes('No authentication')) {
        toast({
          title: 'Chart Loading Failed',
          description: errorMessage,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, [fetchChart, isAuthenticated, navigate, toast]);
  
  const downloadChart = async (endpoint: string, filename: string) => {
    try {
      const response = await fetchWithAuth(`http://localhost:8000${endpoint}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      
    } catch (error) {
      console.error('Error downloading chart:', error);
      
      // Don't show error toast if user was redirected to login
      if (!(error instanceof Error) || 
          (!error.message.includes('Session expired') && 
           !error.message.includes('No authentication'))) {
        toast({
          title: 'Download Failed',
          description: error instanceof Error ? error.message : 'Failed to download chart',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };
  
  useEffect(() => {
    if (isAuthenticated) {
      loadCharts();
    } else {
      // If not authenticated, redirect to login
      navigate('/login');
    }
  }, [isAuthenticated, loadCharts, navigate]);
  
  if (isLoading) {
    return (
      <VStack spacing={6} w="full" align="center" py={8}>
        <Spinner size="xl" color="purple.500" />
        <Text>Loading comparison charts...</Text>
      </VStack>
    );
  }
  
  if (error) {
    return (
      <VStack spacing={6} w="full" align="stretch">
        <Alert status="error">
          <AlertIcon />
          <Box>
            <AlertTitle>Chart Loading Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
        
        <Button
          leftIcon={<FaChartLine />}
          colorScheme="purple"
          onClick={loadCharts}
        >
          Retry Loading Charts
        </Button>
      </VStack>
    );
  }
  
  return (
    <VStack spacing={6} w="full" align="stretch">
      <Heading size="lg" color="purple.600">
        <HStack>
          <FaChartLine />
          <Text>Progress Comparison Charts</Text>
        </HStack>
      </Heading>
      
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Comparison Chart */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <HStack>
                <FaChartLine color="#805AD5" />
                <Heading size="md">Progress Over Time</Heading>
              </HStack>
              <Button
                size="sm"
                leftIcon={<FaDownload />}
                variant="outline"
                onClick={() => downloadChart('/comparison-charts', 'progress_comparison.txt')}
              >
                Download
              </Button>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Text fontSize="sm" color="gray.600">
                Track your clarity, confidence, and speech rate improvements over time
              </Text>
              
              {comparisonChart ? (
                <Box
                  w="full"
                  h="300px"
                  borderRadius="md"
                  overflow="auto"
                  border="1px"
                  borderColor="gray.200"
                  p={4}
                  bg="white"
                >
                  <Text
                    fontFamily="monospace"
                    fontSize="sm"
                    whiteSpace="pre-wrap"
                    color="gray.800"
                  >
                    {comparisonChart}
                  </Text>
                </Box>
              ) : (
                <Box
                  w="full"
                  h="300px"
                  bg="gray.100"
                  borderRadius="md"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text color="gray.500">No comparison data available</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
        
        {/* Language Distribution Chart */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <HStack>
                <FaLanguage color="#805AD5" />
                <Heading size="md">Language Distribution</Heading>
              </HStack>
              <Button
                size="sm"
                leftIcon={<FaDownload />}
                variant="outline"
                onClick={() => downloadChart('/language-charts', 'language_distribution.txt')}
              >
                Download
              </Button>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Text fontSize="sm" color="gray.600">
                See the distribution of languages in your recordings
              </Text>
              
              {languageChart ? (
                <Box
                  w="full"
                  h="300px"
                  borderRadius="md"
                  overflow="auto"
                  border="1px"
                  borderColor="gray.200"
                  p={4}
                  bg="white"
                >
                  <Text
                    fontFamily="monospace"
                    fontSize="sm"
                    whiteSpace="pre-wrap"
                    color="gray.800"
                  >
                    {languageChart}
                  </Text>
                </Box>
              ) : (
                <Box
                  w="full"
                  h="300px"
                  bg="gray.100"
                  borderRadius="md"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text color="gray.500">No language data available</Text>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>
      
      {/* Chart Information */}
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <Heading size="sm" color="purple.600">
              Chart Information
            </Heading>
            
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <Box>
                <Text fontWeight="medium" mb={2}>
                  Progress Comparison Chart
                </Text>
                <Text fontSize="sm" color="gray.600">
                  Shows your improvement in clarity, confidence, and speech rate over time.
                  Each line represents a different metric, helping you track your progress.
                </Text>
              </Box>
              
              <Box>
                <Text fontWeight="medium" mb={2}>
                  Language Distribution Chart
                </Text>
                <Text fontSize="sm" color="gray.600">
                  Displays the distribution of languages detected in your recordings.
                  Helps you understand your multilingual speaking patterns.
                </Text>
              </Box>
            </SimpleGrid>
            
            <HStack justify="center" pt={4}>
              <Button
                leftIcon={<FaChartLine />}
                colorScheme="purple"
                variant="outline"
                onClick={loadCharts}
              >
                Refresh Charts
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
}; 