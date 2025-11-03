import React, { useState, useEffect } from 'react';
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
  Select,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
  Badge,
  SimpleGrid,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { FaLanguage, FaGlobe, FaCheck } from 'react-icons/fa';

interface SupportedLanguages {
  supported_languages: Record<string, string>;
  total_languages: number;
  default_language: string;
}

export const LanguageSettings: React.FC = () => {
  const [supportedLanguages, setSupportedLanguages] = useState<SupportedLanguages | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  useEffect(() => {
    fetchSupportedLanguages();
  }, []);
  
  const fetchSupportedLanguages = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await fetch('http://localhost:8000/supported-languages', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch languages: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSupportedLanguages(data);
      
      // Set current preferred language from localStorage
      const currentLang = localStorage.getItem('preferred_language') || 'en';
      setSelectedLanguage(currentLang);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load languages';
      setError(errorMessage);
      toast({
        title: 'Language Loading Failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleLanguageChange = (languageCode: string) => {
    setSelectedLanguage(languageCode);
    localStorage.setItem('preferred_language', languageCode);
    
    toast({
      title: 'Language Updated',
      description: `Preferred language set to ${supportedLanguages?.supported_languages[languageCode] || languageCode}`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };
  
  if (isLoading) {
    return (
      <VStack spacing={6} w="full" align="center" py={8}>
        <Spinner size="xl" color="purple.500" />
        <Text>Loading supported languages...</Text>
      </VStack>
    );
  }
  
  if (error) {
    return (
      <VStack spacing={6} w="full" align="stretch">
        <Alert status="error">
          <AlertIcon />
          <Box>
            <AlertTitle>Language Loading Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
        
        <Button
          leftIcon={<FaLanguage />}
          colorScheme="purple"
          onClick={fetchSupportedLanguages}
        >
          Retry Loading Languages
        </Button>
      </VStack>
    );
  }
  
  if (!supportedLanguages) {
    return (
      <VStack spacing={6} w="full" align="center" py={8}>
        <Text>No language data available</Text>
      </VStack>
    );
  }
  
  const languageEntries = Object.entries(supportedLanguages.supported_languages);
  
  return (
    <VStack spacing={6} w="full" align="stretch">
      <Heading size="lg" color="purple.600">
        <HStack>
          <FaLanguage />
          <Text>Language Settings</Text>
        </HStack>
      </Heading>
      
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardHeader>
          <Heading size="md">Preferred Language</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <Text fontSize="sm" color="gray.600">
              Select your preferred language for analysis. The system will automatically detect the language of your speech, but you can set a default preference.
            </Text>
            
            <FormControl>
              <FormLabel>Default Language</FormLabel>
              <Select
                value={selectedLanguage}
                onChange={(e) => handleLanguageChange(e.target.value)}
              >
                {languageEntries.map(([code, name]) => (
                  <option key={code} value={code}>
                    {name} ({code.toUpperCase()})
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <HStack>
              <FaCheck color="green" />
              <Text fontSize="sm" color="green.600">
                Current preference: {supportedLanguages.supported_languages[selectedLanguage]}
              </Text>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
      
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardHeader>
          <Heading size="md">
            <HStack>
              <FaGlobe />
              <Text>Supported Languages ({supportedLanguages.total_languages})</Text>
            </HStack>
          </Heading>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {languageEntries.map(([code, name]) => (
              <HStack
                key={code}
                p={3}
                border="1px"
                borderColor={borderColor}
                borderRadius="md"
                bg={selectedLanguage === code ? 'purple.50' : 'transparent'}
                _dark={{
                  bg: selectedLanguage === code ? 'purple.900' : 'transparent'
                }}
              >
                <Badge
                  colorScheme={selectedLanguage === code ? 'purple' : 'gray'}
                  variant={selectedLanguage === code ? 'solid' : 'outline'}
                >
                  {code.toUpperCase()}
                </Badge>
                <Text fontSize="sm">{name}</Text>
                {selectedLanguage === code && <FaCheck color="purple" />}
              </HStack>
            ))}
          </SimpleGrid>
        </CardBody>
      </Card>
      
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <VStack spacing={3} align="stretch">
            <Heading size="sm" color="purple.600">Language Detection Features:</Heading>
            <Text fontSize="sm" color="gray.600">
              • Automatic language detection from speech audio<br/>
              • Support for 4 languages including Indian languages (Hindi, Kannada, Telugu)<br/>
              • Language-specific analysis and recommendations<br/>
              • Transcription in the detected language<br/>
              • Voice cloning detection works across all supported languages
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
}; 