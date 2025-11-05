import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  VStack,
  HStack,
  Progress,
  Badge,
  List,
  ListItem,
  useToast,
  SimpleGrid,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import api from '../config/api';
import { UserProgress, PracticeSession } from '../types';

export const ProgressDashboard: React.FC = () => {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [sessions, setSessions] = useState<PracticeSession[]>([]);
  const [recordings, setRecordings] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const cardBg = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [progressRes, sessionsRes, recordingsRes] = await Promise.all([
          api.get<UserProgress>('/user/progress'),
          api.get<PracticeSession[]>('/practice-sessions'),
          api.get('/user/recordings'),
        ]);

        setProgress(progressRes.data);
        setSessions(sessionsRes.data);
        setRecordings(recordingsRes.data?.recordings || []);
      } catch (error) {
        console.error('Error fetching progress data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load progress data',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [toast]);

  if (isLoading) {
    return (
      <Box p={8} textAlign="center">
        <Text>Loading progress data...</Text>
      </Box>
    );
  }

  const metrics = progress?.latest_metrics || {
    clarity_trend: 0,
    confidence_trend: 0,
    speech_rate_trend: 0,
    emotion_expression_score: 0,
    vocabulary_score: 0,
    overall_improvement: 0,
    current_goals: [],
    completed_goals: [],
    badges_earned: [],
    user_id: '',
    metric_date: new Date().toISOString(),
  } as any;
  
  const trendData = [
    {
      name: 'Clarity',
      value: (metrics.clarity_trend || 0) * 100,
    },
    {
      name: 'Confidence',
      value: (metrics.confidence_trend || 0) * 100,
    },
    {
      name: 'Speech Rate',
      value: (metrics.speech_rate_trend || 0) * 100,
    },
  ];

  return (
    <Box w="full" p={6} bg={bgColor} borderRadius="lg" boxShadow="md" border="1px solid" borderColor={borderColor}>
      <VStack spacing={8} align="stretch">
        <Heading size="lg" color="purple.600">
          Your Voice Analytics Progress
        </Heading>
        {!progress?.latest_metrics && (
          <Box p={4} borderRadius="md" bg={cardBg} border="1px solid" borderColor={borderColor}>
            <Text color={textColor}>
              No progress metrics yet. Record or upload an audio in Quick/Enhanced Analysis to generate your first metrics.
            </Text>
          </Box>
        )}

        <SimpleGrid columns={[1, 2, 3]} spacing={6}>
          <Box p={4} borderRadius="md" bg={cardBg} border="1px solid" borderColor={borderColor}>
            <Text fontSize="lg" fontWeight="semibold" mb={2}>
              Overall Improvement
            </Text>
            <Progress
              value={(metrics.overall_improvement || 0) * 100}
              colorScheme="green"
              size="lg"
              borderRadius="full"
            />
            <Text mt={2} fontSize="sm" color={textColor}>
              {((metrics.overall_improvement || 0) * 100).toFixed(1)}%
            </Text>
          </Box>

          <Box p={4} borderRadius="md" bg={cardBg} border="1px solid" borderColor={borderColor}>
            <Text fontSize="lg" fontWeight="semibold" mb={2}>
              Total Recordings
            </Text>
            <Text fontSize="3xl" fontWeight="bold" color="purple.500">
              {progress?.total_recordings || recordings.length || 0}
            </Text>
          </Box>

          <Box p={4} borderRadius="md" bg={cardBg} border="1px solid" borderColor={borderColor}>
            <Text fontSize="lg" fontWeight="semibold" mb={2}>
              Latest Emotion Score
            </Text>
            <Progress
              value={(metrics.emotion_expression_score || 0) * 100}
              colorScheme="blue"
              size="lg"
              borderRadius="full"
            />
            <Text mt={2} fontSize="sm" color={textColor}>
              {((metrics.emotion_expression_score || 0) * 100).toFixed(1)}%
            </Text>
          </Box>
        </SimpleGrid>

        <Box h="300px" w="100%" minH="300px" position="relative">
          <Text fontSize="lg" fontWeight="semibold" mb={4}>
            Progress Trends
          </Text>
          <Box position="absolute" top="40px" bottom="0" left="0" right="0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#805AD5"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </Box>

        <Box>
          <Text fontSize="lg" fontWeight="semibold" mb={4}>
            Current Goals
          </Text>
          <List spacing={3}>
            {(metrics.current_goals || []).map((goal, index) => {
              const goalKey = goal ? `${goal.substring(0, 20).replace(/\s+/g, '-')}-${index}` : `goal-${index}`;
              return (
                <ListItem key={goalKey}>
                  <HStack>
                    <Badge colorScheme="purple">Goal {index + 1}</Badge>
                    <Text>{goal}</Text>
                  </HStack>
                </ListItem>
              );
            })}
          </List>
        </Box>

        <Box>
          <Text fontSize="lg" fontWeight="semibold" mb={4}>
            Recent Practice Sessions
          </Text>
          <Grid templateColumns={['1fr', '1fr', 'repeat(2, 1fr)']} gap={4}>
            {sessions.slice(0, 4).map((session) => (
              <Box
                key={session.id}
                p={4}
                borderRadius="md"
                bg={cardBg}
                border="1px"
                borderColor={borderColor}
              >
                <VStack align="start" spacing={2}>
                  <Badge colorScheme="green">{session.session_type}</Badge>
                  <Text fontWeight="semibold">{session.topic}</Text>
                  <Text fontSize="sm" color={textColor}>
                    Clarity: {((session.average_clarity || 0) * 100).toFixed(1)}%
                  </Text>
                  <Text fontSize="sm" color={textColor}>
                    Confidence: {((session.average_confidence || 0) * 100).toFixed(1)}%
                  </Text>
                  <Text fontSize="sm" color={textColor}>
                    Dominant Emotion: {session.dominant_emotion || 'N/A'}
                  </Text>
                </VStack>
              </Box>
            ))}
          </Grid>
        </Box>

        <Box>
          <Text fontSize="lg" fontWeight="semibold" mb={4}>
            Recent Recordings
          </Text>
          <Grid templateColumns={['1fr', '1fr', 'repeat(2, 1fr)']} gap={4}>
            {(recordings || []).slice(0, 4).map((r: any) => (
              <Box
                key={r.id || r._id}
                p={4}
                borderRadius="md"
                bg={cardBg}
                border="1px"
                borderColor={borderColor}
              >
                <VStack align="start" spacing={2}>
                  <Badge colorScheme="purple">{r.session_type}</Badge>
                  <Text fontWeight="semibold">{r.topic}</Text>
                  <Text fontSize="sm" color={textColor}>
                    {r.created_at ? new Date(r.created_at).toLocaleString() : ''}
                  </Text>
                </VStack>
              </Box>
            ))}
            {(!recordings || recordings.length === 0) && (
              <Text color={textColor}>No recordings yet.</Text>
            )}
          </Grid>
        </Box>

        {metrics.badges_earned && metrics.badges_earned.length > 0 && (
          <Box>
            <Text fontSize="lg" fontWeight="semibold" mb={4}>
              Achievements
            </Text>
            <SimpleGrid columns={[2, 3, 4]} spacing={4}>
              {metrics.badges_earned.map((badge) => (
                <Box
                  key={badge.id}
                  p={4}
                  borderRadius="md"
                  bg="purple.50"
                  textAlign="center"
                >
                  <VStack spacing={2}>
                    <Text fontWeight="bold">{badge.name}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {badge.description}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Earned: {new Date(badge.earned_date).toLocaleDateString()}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </Box>
        )}
      </VStack>
    </Box>
  );
}; 