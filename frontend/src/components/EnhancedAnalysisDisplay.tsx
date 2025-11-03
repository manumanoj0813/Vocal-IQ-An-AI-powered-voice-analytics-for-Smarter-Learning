import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Progress,
  Badge,
  Card,
  CardBody,
  Heading,
  Divider,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue,
  Tooltip,
  Icon,
  Button,
  useToast,
} from '@chakra-ui/react';
import { FaMicrophone, FaChartLine, FaLightbulb, FaStar, FaDownload } from 'react-icons/fa';
import { VoiceAnalysis } from '../types';
import api from '../config/api';

interface EnhancedAnalysisDisplayProps {
  analysis: VoiceAnalysis;
}

export const EnhancedAnalysisDisplay: React.FC<EnhancedAnalysisDisplayProps> = ({ analysis }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const toast = useToast();

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'yellow';
    return 'red';
  };

  const getEmotionColor = (emotion: string) => {
    const colors: { [key: string]: string } = {
      happy: 'green',
      excited: 'orange',
      calm: 'blue',
      sad: 'purple',
      angry: 'red',
      neutral: 'gray',
    };
    return colors[emotion] || 'gray';
  };

  const formatScore = (score: number) => `${Math.round(score * 100)}%`;
  const formatPitch = (pitch: number) => `${Math.round(pitch)} Hz`;
  const formatTempo = (tempo: number) => `${Math.round(tempo)} WPM`;

  const handleDownloadPDF = async () => {
    try {
      const response = await api.post('/export-analysis-pdf', analysis, {
        responseType: 'blob',
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from response headers or create default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'enhanced_voice_analysis_report.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: 'PDF Downloaded',
        description: 'Your enhanced voice analysis report has been downloaded successfully!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast({
        title: 'Download Failed',
        description: 'Failed to download PDF. Please try again.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <VStack spacing={6} w="full" align="stretch">
      {/* Overall Confidence Score */}
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <HStack justify="space-between" mb={4}>
            <Heading size="md" color="purple.600">
              <Icon as={FaStar} mr={2} />
              Analysis Confidence
            </Heading>
            <HStack spacing={3}>
              <Button
                leftIcon={<FaDownload />}
                colorScheme="purple"
                variant="outline"
                size="sm"
                onClick={handleDownloadPDF}
                _hover={{ bg: 'purple.50' }}
              >
                Download PDF
              </Button>
              <Badge
                colorScheme={getConfidenceColor(analysis.audio_metrics.confidence_score)}
                fontSize="lg"
                px={3}
                py={1}
              >
                {formatScore(analysis.audio_metrics.confidence_score)}
              </Badge>
            </HStack>
          </HStack>
          <Progress
            value={analysis.audio_metrics.confidence_score * 100}
            colorScheme={getConfidenceColor(analysis.audio_metrics.confidence_score)}
            size="lg"
            borderRadius="md"
          />
        </CardBody>
      </Card>

      {/* Enhanced Metrics Grid */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={6}>
        {/* Pitch Analysis */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="sm" color="purple.600" mb={4}>
              <Icon as={FaMicrophone} mr={2} />
              Pitch Analysis
            </Heading>
            <VStack spacing={3} align="stretch">
              <Stat>
                <StatLabel>Average Pitch</StatLabel>
                <StatNumber fontSize="lg">{formatPitch(analysis.audio_metrics.pitch.average_pitch)}</StatNumber>
                <StatHelpText>Range: {formatPitch(analysis.audio_metrics.pitch.range_min)} - {formatPitch(analysis.audio_metrics.pitch.range_max)}</StatHelpText>
              </Stat>
              <Divider />
              <HStack justify="space-between">
                <Text fontSize="sm">Stability</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.pitch.pitch_stability)}>
                  {formatScore(analysis.audio_metrics.pitch.pitch_stability)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Contour Score</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.pitch.pitch_contour)}>
                  {formatScore(analysis.audio_metrics.pitch.pitch_contour)}
                </Badge>
              </HStack>
              {analysis.audio_metrics.pitch.range_semitones && (
                <HStack justify="space-between">
                  <Text fontSize="sm">Range (Semitones)</Text>
                  <Text fontSize="sm" fontWeight="bold">
                    {Math.round(analysis.audio_metrics.pitch.range_semitones)}
                  </Text>
                </HStack>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Rhythm Analysis */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="sm" color="purple.600" mb={4}>
              <Icon as={FaChartLine} mr={2} />
              Rhythm Analysis
            </Heading>
            <VStack spacing={3} align="stretch">
              <Stat>
                <StatLabel>Speech Rate</StatLabel>
                <StatNumber fontSize="lg">{formatScore(analysis.audio_metrics.rhythm.speech_rate)}</StatNumber>
                <StatHelpText>
                  {analysis.audio_metrics.rhythm.speaking_tempo && 
                    `~${formatTempo(analysis.audio_metrics.rhythm.speaking_tempo)}`
                  }
                </StatHelpText>
              </Stat>
              <Divider />
              <HStack justify="space-between">
                <Text fontSize="sm">Pause Ratio</Text>
                <Badge colorScheme={analysis.audio_metrics.rhythm.pause_ratio > 0.3 ? 'red' : 'green'}>
                  {formatScore(analysis.audio_metrics.rhythm.pause_ratio)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Consistency</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.rhythm.rhythm_consistency)}>
                  {formatScore(analysis.audio_metrics.rhythm.rhythm_consistency)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Stress Pattern</Text>
                <Badge colorScheme="blue" variant="outline">
                  {analysis.audio_metrics.rhythm.stress_pattern}
                </Badge>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Clarity Analysis */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="sm" color="purple.600" mb={4}>
              <Icon as={FaMicrophone} mr={2} />
              Clarity Analysis
            </Heading>
            <VStack spacing={3} align="stretch">
              <Stat>
                <StatLabel>Overall Clarity</StatLabel>
                <StatNumber fontSize="lg">{formatScore(analysis.audio_metrics.clarity.overall_clarity || analysis.audio_metrics.clarity.clarity_score)}</StatNumber>
                <StatHelpText>Based on multiple factors</StatHelpText>
              </Stat>
              <Divider />
              <HStack justify="space-between">
                <Text fontSize="sm">Enunciation</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.clarity.enunciation_quality)}>
                  {formatScore(analysis.audio_metrics.clarity.enunciation_quality)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Projection</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.clarity.voice_projection)}>
                  {formatScore(analysis.audio_metrics.clarity.voice_projection)}
                </Badge>
              </HStack>
              {analysis.audio_metrics.clarity.speech_errors && analysis.audio_metrics.clarity.speech_errors.length > 0 && (
                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={2}>Issues Detected:</Text>
                  {analysis.audio_metrics.clarity.speech_errors.map((error, index) => (
                    <Text key={index} fontSize="xs" color="red.500">• {error}</Text>
                  ))}
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Emotion Analysis */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="sm" color="purple.600" mb={4}>
              <Icon as={FaChartLine} mr={2} />
              Emotion Analysis
            </Heading>
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <Text fontSize="sm">Dominant Emotion</Text>
                <Badge colorScheme={getEmotionColor(analysis.audio_metrics.emotion.dominant_emotion)}>
                  {analysis.audio_metrics.emotion.dominant_emotion}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Confidence</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.emotion.emotion_confidence)}>
                  {formatScore(analysis.audio_metrics.emotion.emotion_confidence)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Range</Text>
                <Badge colorScheme="blue" variant="outline">
                  {analysis.audio_metrics.emotion.emotional_range}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Stability</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.emotion.emotional_stability)}>
                  {formatScore(analysis.audio_metrics.emotion.emotional_stability)}
                </Badge>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Fluency Analysis */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="sm" color="purple.600" mb={4}>
              <Icon as={FaChartLine} mr={2} />
              Fluency Analysis
            </Heading>
            <VStack spacing={3} align="stretch">
              <Stat>
                <StatLabel>Fluency Score</StatLabel>
                <StatNumber fontSize="lg">{formatScore(analysis.audio_metrics.fluency.fluency_score)}</StatNumber>
                <StatHelpText>Overall fluency rating</StatHelpText>
              </Stat>
              <Divider />
              <HStack justify="space-between">
                <Text fontSize="sm">Smoothness</Text>
                <Badge colorScheme={getConfidenceColor(analysis.audio_metrics.fluency.smoothness)}>
                  {formatScore(analysis.audio_metrics.fluency.smoothness)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Hesitations</Text>
                <Badge colorScheme={analysis.audio_metrics.fluency.hesitations > 0.3 ? 'red' : 'green'}>
                  {formatScore(analysis.audio_metrics.fluency.hesitations)}
                </Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Repetitions</Text>
                <Badge colorScheme={analysis.audio_metrics.fluency.repetitions > 0.4 ? 'red' : 'green'}>
                  {formatScore(analysis.audio_metrics.fluency.repetitions)}
                </Badge>
              </HStack>
              {analysis.audio_metrics.fluency.fluency_issues && analysis.audio_metrics.fluency.fluency_issues.length > 0 && (
                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={2}>Issues:</Text>
                  {analysis.audio_metrics.fluency.fluency_issues.map((issue, index) => (
                    <Text key={index} fontSize="xs" color="orange.500">• {issue}</Text>
                  ))}
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Transcription */}
        <Card bg={bgColor} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="sm" color="purple.600" mb={4}>
              <Icon as={FaMicrophone} mr={2} />
              Transcription
            </Heading>
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <Text fontSize="sm">Word Count</Text>
                <Text fontSize="sm" fontWeight="bold">
                  {analysis.transcription.word_count}
                </Text>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Confidence</Text>
                <Badge colorScheme={getConfidenceColor(analysis.transcription.transcription_confidence)}>
                  {formatScore(analysis.transcription.transcription_confidence)}
                </Badge>
              </HStack>
              <Divider />
              <Box>
                <Text fontSize="sm" fontWeight="bold" mb={2}>Transcribed Text:</Text>
                <Text fontSize="sm" color={textColor} bg="gray.50" p={3} borderRadius="md" maxH="100px" overflowY="auto">
                  {analysis.transcription.full_text || "No transcription available"}
                </Text>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </Grid>

      {/* Recommendations */}
      <Card bg={bgColor} border="1px" borderColor={borderColor}>
        <CardBody>
          <Heading size="md" color="purple.600" mb={4}>
            <Icon as={FaLightbulb} mr={2} />
            AI Recommendations
          </Heading>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
            <Box>
              <Text fontWeight="bold" mb={3} color="green.600">Key Strengths:</Text>
              <VStack align="start" spacing={2}>
                {analysis.recommendations.strengths.map((strength, index) => (
                  <HStack key={index}>
                    <Icon as={FaStar} color="green.500" />
                    <Text fontSize="sm">{strength}</Text>
                  </HStack>
                ))}
              </VStack>
            </Box>
            <Box>
              <Text fontWeight="bold" mb={3} color="orange.600">Areas for Improvement:</Text>
              <VStack align="start" spacing={2}>
                {analysis.recommendations.improvement_areas.map((area, index) => (
                  <HStack key={index}>
                    <Icon as={FaLightbulb} color="orange.500" />
                    <Text fontSize="sm">{area}</Text>
                  </HStack>
                ))}
              </VStack>
            </Box>
          </Grid>
          <Divider my={4} />
          <Box>
            <Text fontWeight="bold" mb={3} color="blue.600">Practice Suggestions:</Text>
            <VStack align="start" spacing={2}>
              {analysis.recommendations.practice_suggestions.map((suggestion, index) => (
                <HStack key={index}>
                  <Icon as={FaMicrophone} color="blue.500" />
                  <Text fontSize="sm">{suggestion}</Text>
                </HStack>
              ))}
            </VStack>
          </Box>
        </CardBody>
      </Card>
    </VStack>
  );
}; 