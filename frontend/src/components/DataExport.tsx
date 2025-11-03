import React, { useState } from 'react';
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
  FormControl,
  FormLabel,
  Checkbox,
  Select,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
  Divider,
} from '@chakra-ui/react';
import { FaDownload, FaFilePdf, FaFileCsv, FaCalendar } from 'react-icons/fa';

interface ExportRequest {
  format: 'csv' | 'pdf';
  date_range?: {
    start: string;
    end: string;
  };
  include_transcriptions: boolean;
  include_voice_cloning: boolean;
}

export const DataExport: React.FC = () => {
  const [exportRequest, setExportRequest] = useState<ExportRequest>({
    format: 'csv',
    include_transcriptions: true,
    include_voice_cloning: true,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleExport = async () => {
    setIsExporting(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await fetch('http://localhost:8000/export-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(exportRequest),
      });
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }
      
      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vocal_iq_export_${new Date().toISOString().split('T')[0]}.${exportRequest.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: 'Export Successful',
        description: `Your data has been exported as ${exportRequest.format.toUpperCase()}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      setError(errorMessage);
      toast({
        title: 'Export Failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsExporting(false);
    }
  };
  
  return (
    <VStack spacing={6} w="full" align="stretch">
      <Heading size="lg" color="purple.600">
        <HStack>
          <FaDownload />
          <Text>Export Analysis Data</Text>
        </HStack>
      </Heading>
      
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardHeader>
          <Heading size="md">Export Options</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            {error && (
              <Alert status="error">
                <AlertIcon />
                <Box>
                  <AlertTitle>Export Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Box>
              </Alert>
            )}
            
            {/* Format Selection */}
            <FormControl>
              <FormLabel>Export Format</FormLabel>
              <Select
                value={exportRequest.format}
                onChange={(e) => setExportRequest({
                  ...exportRequest,
                  format: e.target.value as 'csv' | 'pdf'
                })}
              >
                <option value="csv">CSV (Spreadsheet)</option>
                <option value="pdf">PDF (Report)</option>
              </Select>
            </FormControl>
            
            <Divider />
            
            {/* Date Range */}
            <FormControl>
              <FormLabel>
                <HStack>
                  <FaCalendar />
                  <Text>Date Range (Optional)</Text>
                </HStack>
              </FormLabel>
              <HStack>
                <input
                  type="date"
                  onChange={(e) => setExportRequest({
                    ...exportRequest,
                    date_range: {
                      ...exportRequest.date_range,
                      start: e.target.value
                    }
                  })}
                  style={{
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    backgroundColor: 'white'
                  }}
                />
                <Text>to</Text>
                <input
                  type="date"
                  onChange={(e) => setExportRequest({
                    ...exportRequest,
                    date_range: {
                      ...exportRequest.date_range,
                      end: e.target.value
                    }
                  })}
                  style={{
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    backgroundColor: 'white'
                  }}
                />
              </HStack>
            </FormControl>
            
            <Divider />
            
            {/* Export Options */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold">Include in Export:</Text>
              
              <Checkbox
                isChecked={exportRequest.include_transcriptions}
                onChange={(e) => setExportRequest({
                  ...exportRequest,
                  include_transcriptions: e.target.checked
                })}
              >
                Transcriptions and Language Detection
              </Checkbox>
              
              <Checkbox
                isChecked={exportRequest.include_voice_cloning}
                onChange={(e) => setExportRequest({
                  ...exportRequest,
                  include_voice_cloning: e.target.checked
                })}
              >
                Voice Cloning Detection Results
              </Checkbox>
            </VStack>
            
            <Divider />
            
            {/* Export Button */}
            <Button
              leftIcon={isExporting ? <Spinner size="sm" /> : (exportRequest.format === 'pdf' ? <FaFilePdf /> : <FaFileCsv />)}
              colorScheme="purple"
              size="lg"
              onClick={handleExport}
              isLoading={isExporting}
              loadingText="Exporting..."
            >
              Export as {exportRequest.format.toUpperCase()}
            </Button>
          </VStack>
        </CardBody>
      </Card>
      
      {/* Export Information */}
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <VStack spacing={3} align="stretch">
            <Heading size="sm" color="purple.600">What's Included:</Heading>
            <Text fontSize="sm" color="gray.600">
              • Basic recording information (date, session type, topic)<br/>
              • Audio metrics (clarity, confidence, speech rate, emotions)<br/>
              • Language detection results (if enabled)<br/>
              • Voice cloning detection (if enabled)<br/>
              • Transcriptions (if enabled)<br/>
              • Progress tracking data
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
}; 