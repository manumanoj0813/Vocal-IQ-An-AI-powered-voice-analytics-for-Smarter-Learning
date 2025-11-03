import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  Select,
  Textarea,
  useToast,
  Progress,
  Badge,
  HStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { AudioRecorder } from './AudioRecorder';
import { VoiceAnalysis } from '../types';

const PRACTICE_TOPICS = {
  interview: [
    'Tell me about yourself',
    'Why are you interested in this position?',
    'Describe a challenging situation you faced',
    'What are your strengths and weaknesses?',
    'Where do you see yourself in 5 years?',
  ],
  presentation: [
    'Introduction to your favorite hobby',
    'A technology that excites you',
    'A memorable travel experience',
    'A recent learning experience',
    'Your professional journey',
  ],
  reading: [
    'The importance of effective communication',
    'Technology in modern society',
    'Environmental challenges and solutions',
    'Cultural diversity in the workplace',
    'Leadership and teamwork',
  ],
};

interface PracticeSessionProps {
  onAnalysisComplete: (analysis: VoiceAnalysis) => void;
}

export const PracticeSession: React.FC<PracticeSessionProps> = ({ onAnalysisComplete }) => {
  const [sessionType, setSessionType] = useState<keyof typeof PRACTICE_TOPICS>('interview');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [customTopic, setCustomTopic] = useState('');
  const [currentAnalysis, setCurrentAnalysis] = useState<VoiceAnalysis | null>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const topicBg = useColorModeValue('purple.50', 'purple.900');

  const handleStartSession = () => {
    if (!sessionType || (!selectedTopic && !customTopic)) {
      toast({
        title: 'Error',
        description: 'Please select a session type and topic',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    setIsSessionActive(true);
  };

  const handleAnalysisComplete = (analysis: VoiceAnalysis) => {
    setCurrentAnalysis(analysis);
    onAnalysisComplete(analysis);
  };

  const getEmotionColor = (emotion: string) => {
    const emotionColors: Record<string, string> = {
      happy: 'green',
      confident: 'blue',
      neutral: 'gray',
      nervous: 'orange',
      uncertain: 'yellow',
    };
    return emotionColors[emotion.toLowerCase()] || 'purple';
  };

  return (
    <Box w="full" p={6} bg={bgColor} borderRadius="lg" boxShadow="md" border="1px solid" borderColor={borderColor}>
      <VStack spacing={6} align="stretch">
        <Heading size="lg" color="purple.600">
          Practice Session
        </Heading>

        {!isSessionActive ? (
          <VStack spacing={4} align="stretch">
            <Box>
              <Text mb={2} fontWeight="semibold">
                Select Session Type
              </Text>
              <Select
                value={sessionType}
                onChange={(e) => setSessionType(e.target.value as keyof typeof PRACTICE_TOPICS)}
              >
                <option value="interview">Interview Practice</option>
                <option value="presentation">Presentation Skills</option>
                <option value="reading">Reading Exercise</option>
              </Select>
            </Box>

            <Box>
              <Text mb={2} fontWeight="semibold">
                Select Topic
              </Text>
              <Select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                mb={2}
              >
                <option value="">Choose a topic or create your own</option>
                {PRACTICE_TOPICS[sessionType].map((topic) => (
                  <option key={topic} value={topic}>
                    {topic}
                  </option>
                ))}
              </Select>

              <Text mb={2} fontWeight="semibold">
                Or Create Custom Topic
              </Text>
              <Textarea
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                placeholder="Enter your own topic or prompt..."
                size="sm"
              />
            </Box>

            <Button
              colorScheme="purple"
              size="lg"
              onClick={handleStartSession}
              isDisabled={!sessionType || (!selectedTopic && !customTopic)}
            >
              Start Practice Session
            </Button>
          </VStack>
        ) : (
          <VStack spacing={6} align="stretch">
            <Box p={4} bg={topicBg} borderRadius="md" border="1px solid" borderColor={borderColor}>
              <Text fontWeight="semibold" mb={2}>
                Current Topic:
              </Text>
              <Text>{selectedTopic || customTopic}</Text>
            </Box>

            <AudioRecorder
              onAnalysisComplete={handleAnalysisComplete}
              sessionType={sessionType}
              topic={selectedTopic || customTopic}
            />

            {currentAnalysis && (
              <VStack spacing={4} align="stretch" mt={4}>
                <Heading size="md" color="purple.600">
                  Real-time Analysis
                </Heading>

                <HStack spacing={4}>
                  <Badge
                    colorScheme={getEmotionColor(
                      currentAnalysis.audio_metrics.emotion.dominant_emotion
                    )}
                    p={2}
                    borderRadius="md"
                  >
                    {currentAnalysis.audio_metrics.emotion.dominant_emotion}
                  </Badge>
                  <Text fontSize="sm">
                    Confidence:{' '}
                    {(
                      currentAnalysis.audio_metrics.emotion.emotion_confidence * 100
                    ).toFixed(1)}
                    %
                  </Text>
                </HStack>

                <Box>
                  <Text mb={1}>Clarity</Text>
                  <Progress
                    value={
                      currentAnalysis.audio_metrics.clarity.clarity_score * 100
                    }
                    colorScheme="green"
                  />
                </Box>

                <Box>
                  <Text mb={1}>Speech Rate</Text>
                  <Progress
                    value={
                      currentAnalysis.audio_metrics.rhythm.speech_rate * 33
                    }
                    colorScheme="blue"
                  />
                </Box>

                <Box>
                  <Text mb={1}>Articulation</Text>
                  <Progress
                    value={
                      currentAnalysis.audio_metrics.clarity.articulation_rate *
                      100
                    }
                    colorScheme="purple"
                  />
                </Box>

                <Box>
                  <Text fontWeight="semibold" mb={2}>
                    Recommendations:
                  </Text>
                  <VStack align="stretch" spacing={2}>
                    {currentAnalysis.recommendations.key_points.map((rec: string, index: number) => (
                      <Text key={index} fontSize="sm">
                        • {rec}
                      </Text>
                    ))}
                  </VStack>
                </Box>
              </VStack>
            )}

            <Button
              colorScheme="red"
              variant="outline"
              onClick={() => setIsSessionActive(false)}
            >
              End Session
            </Button>
          </VStack>
        )}
      </VStack>
    </Box>
  );
}; 