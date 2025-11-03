import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Badge,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Card,
  CardBody,
  CardHeader,
  Heading,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { FaLanguage, FaShieldAlt, FaFileExport, FaChartBar } from 'react-icons/fa';
import { VoiceAnalysis } from '../types';
import { EnhancedAnalysisDisplay } from './EnhancedAnalysisDisplay';

interface EnhancedAnalysisProps {
  analysis: VoiceAnalysis;
}

export const EnhancedAnalysis: React.FC<EnhancedAnalysisProps> = ({ analysis }) => {
  const [isExporting, setIsExporting] = useState(false);
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const enhancedFeatures = analysis.enhanced_features;
  
  if (!enhancedFeatures) {
    return (
      <Alert status="info">
        <AlertIcon />
        <AlertTitle>Enhanced Analysis</AlertTitle>
        <AlertDescription>
          Enhanced analysis features are not available for this recording.
        </AlertDescription>
      </Alert>
    );
  }
  
  const languageDetection = enhancedFeatures.language_detection;
  const voiceCloningDetection = enhancedFeatures.voice_cloning_detection;
  
  const handleExport = async (format: 'csv' | 'pdf') => {
    setIsExporting(true);
    try {
      const response = await fetch('/export-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          format,
          include_transcriptions: true,
          include_voice_cloning: true,
        }),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vocal_iq_analysis.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast({
          title: 'Export Successful',
          description: `Analysis data exported as ${format.toUpperCase()}`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      toast({
        title: 'Export Failed',
        description: 'Failed to export analysis data',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsExporting(false);
    }
  };
  
  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return 'red';
      case 'medium':
        return 'orange';
      case 'low':
        return 'green';
      default:
        return 'gray';
    }
  };
  
  const getDetectionStatus = (isAiGenerated: boolean) => {
    return isAiGenerated ? 'AI Generated' : 'Human Voice';
  };
  
  const getDetectionColor = (isAiGenerated: boolean) => {
    return isAiGenerated ? 'red' : 'green';
  };
  
  return (
    <VStack spacing={6} w="full" align="stretch">
      <Tabs variant="soft-rounded" colorScheme="purple" w="full">
        <TabList justifyContent="center" mb={6}>
          <Tab>
            <HStack>
              <FaChartBar />
              <Text>Enhanced Analysis</Text>
            </HStack>
          </Tab>
          <Tab>
            <HStack>
              <FaLanguage />
              <Text>Language & Security</Text>
            </HStack>
          </Tab>
        </TabList>

        <TabPanels>
          {/* Enhanced Analysis Tab */}
          <TabPanel>
            <EnhancedAnalysisDisplay analysis={analysis} />
          </TabPanel>

          {/* Language & Security Tab */}
          <TabPanel>
            <VStack spacing={6} w="full" align="stretch">
              <Heading size="md" color="purple.600">
                <HStack>
                  <FaLanguage />
                  <Text>Enhanced Analysis Features</Text>
                </HStack>
              </Heading>
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                {/* Language Detection */}
                <Card bg={bgColor} border="1px" borderColor={borderColor}>
                  <CardHeader>
                    <HStack>
                      <FaLanguage color="#805AD5" />
                      <Heading size="sm">Language Detection</Heading>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Stat>
                        <StatLabel>Detected Language</StatLabel>
                        <StatNumber fontSize="2xl">
                          {languageDetection?.language_name || 'Unknown'}
                        </StatNumber>
                        <StatHelpText>
                          Code: {languageDetection?.language_code || 'N/A'}
                        </StatHelpText>
                      </Stat>
                      
                      <Box>
                        <Text fontSize="sm" fontWeight="medium" mb={2}>
                          Confidence Level
                        </Text>
                        <Progress
                          value={(languageDetection?.confidence || 0) * 100}
                          colorScheme="purple"
                          size="sm"
                          borderRadius="md"
                        />
                        <Text fontSize="xs" mt={1} color="gray.500">
                          {(languageDetection?.confidence || 0) * 100}% confidence
                        </Text>
                      </Box>
                      
                      {languageDetection?.transcription && (
                        <Box>
                          <Text fontSize="sm" fontWeight="medium" mb={2}>
                            Transcription
                          </Text>
                          <Text
                            fontSize="sm"
                            p={3}
                            bg="gray.50"
                            borderRadius="md"
                            border="1px"
                            borderColor="gray.200"
                          >
                            {languageDetection.transcription}
                          </Text>
                        </Box>
                      )}
                    </VStack>
                  </CardBody>
                </Card>
                
                {/* Voice Cloning Detection */}
                <Card bg={bgColor} border="1px" borderColor={borderColor}>
                  <CardHeader>
                    <HStack>
                      <FaShieldAlt color="#805AD5" />
                      <Heading size="sm">Voice Cloning Detection</Heading>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Stat>
                        <StatLabel>Detection Result</StatLabel>
                        <StatNumber fontSize="2xl">
                          <Badge
                            colorScheme={getDetectionColor(voiceCloningDetection?.is_ai_generated || false)}
                            fontSize="md"
                            p={2}
                          >
                            {getDetectionStatus(voiceCloningDetection?.is_ai_generated || false)}
                          </Badge>
                        </StatNumber>
                        <StatHelpText>
                          Method: {voiceCloningDetection?.detection_method || 'N/A'}
                        </StatHelpText>
                      </Stat>
                      
                      <Box>
                        <Text fontSize="sm" fontWeight="medium" mb={2}>
                          AI Detection Score
                        </Text>
                        <Progress
                          value={(voiceCloningDetection?.confidence_score || 0) * 100}
                          colorScheme={getDetectionColor(voiceCloningDetection?.is_ai_generated || false)}
                          size="sm"
                          borderRadius="md"
                        />
                        <Text fontSize="xs" mt={1} color="gray.500">
                          {(voiceCloningDetection?.confidence_score || 0) * 100}% confidence
                        </Text>
                      </Box>
                      
                      <Box>
                        <Text fontSize="sm" fontWeight="medium" mb={2}>
                          Risk Level
                        </Text>
                        <Badge
                          colorScheme={getRiskLevelColor(voiceCloningDetection?.risk_level || 'low')}
                          fontSize="sm"
                          p={2}
                          textTransform="capitalize"
                        >
                          {voiceCloningDetection?.risk_level || 'low'} risk
                        </Badge>
                      </Box>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
              
              {/* Export Options */}
              <Card bg={bgColor} border="1px" borderColor={borderColor}>
                <CardHeader>
                  <HStack>
                    <FaFileExport color="#805AD5" />
                    <Heading size="sm">Export Analysis Data</Heading>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4}>
                    <Text fontSize="sm" color="gray.600">
                      Export your analysis results including language detection and voice cloning analysis
                    </Text>
                    
                    <HStack spacing={4}>
                      <Button
                        leftIcon={<FaFileExport />}
                        colorScheme="blue"
                        variant="outline"
                        onClick={() => handleExport('csv')}
                        isLoading={isExporting}
                        loadingText="Exporting CSV..."
                      >
                        Export as CSV
                      </Button>
                      
                      <Button
                        leftIcon={<FaFileExport />}
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleExport('pdf')}
                        isLoading={isExporting}
                        loadingText="Exporting PDF..."
                      >
                        Export as PDF
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
              
              {/* Enhanced Features Status */}
              <Alert status="success">
                <AlertIcon />
                <Box>
                  <AlertTitle>Enhanced Features Active</AlertTitle>
                  <AlertDescription>
                    This analysis includes advanced language detection and AI voice cloning detection.
                    All features are working correctly.
                  </AlertDescription>
                </Box>
              </Alert>
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
}; 