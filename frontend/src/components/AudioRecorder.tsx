import React, { useState, useRef, useEffect } from 'react'
import { 
  VStack, 
  Text, 
  useToast, 
  Box, 
  Progress, 
  HStack, 
  Button, 
  Icon, 
  useColorModeValue, 
} from '@chakra-ui/react'
import { FaMicrophone, FaStop, FaExclamationTriangle, FaDownload } from 'react-icons/fa'
import api from '../config/api'
import { AudioRecorderProps, VoiceAnalysis } from '../types'
import { handleApiError } from '../utils/errorHandler'

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ 
  onAnalysisComplete, 
  sessionType = 'practice', 
  topic = 'general' 
}) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const toast = useToast()
  const [lastAudioBlob, setLastAudioBlob] = useState<Blob | null>(null)
  const [lastAudioUrl, setLastAudioUrl] = useState<string | null>(null)

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const errorBg = useColorModeValue('red.50', 'red.900')
  const errorColor = useColorModeValue('red.600', 'red.300')

  const mimeType = 'audio/webm'

  useEffect(() => {
    checkMicrophonePermission()
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  const checkMicrophonePermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop())
      setHasPermission(true)
    } catch (error) {
      console.error('Microphone permission error:', error)
      setHasPermission(false)
    }
  }

  const setupAudioAnalyser = (stream: MediaStream) => {
    audioContextRef.current = new AudioContext()
    analyserRef.current = audioContextRef.current.createAnalyser()
    const source = audioContextRef.current.createMediaStreamSource(stream)
    source.connect(analyserRef.current)
    analyserRef.current.fftSize = 256

    const levelInterval = setInterval(() => {
      if (analyserRef.current) {
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
        analyserRef.current.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        setAudioLevel(average)
      }
    }, 100)

    return levelInterval
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType })
      chunksRef.current = []

      const levelInterval = setupAudioAnalyser(stream)

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        stream.getTracks().forEach(track => track.stop())
        clearInterval(levelInterval)
        try {
          setIsProcessing(true)
          const audioBlob = new Blob(chunksRef.current, { type: mimeType })
          setLastAudioBlob(audioBlob)
          if (lastAudioUrl) {
            URL.revokeObjectURL(lastAudioUrl)
          }
          setLastAudioUrl(URL.createObjectURL(audioBlob))
          await sendAudioForAnalysis(audioBlob)
        } catch (error) {
          console.error('Error processing audio:', error)
          const toastOptions = handleApiError(error)
          toast(toastOptions)
        } finally {
          setIsProcessing(false)
          setRecordingTime(0)
        }
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

      toast({
        title: 'Recording Started',
        description: 'Speak clearly into your microphone.',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })

    } catch (error) {
      console.error('Microphone access error:', error)
      toast({
        title: 'Error',
        description: 'Could not access microphone. Please check permissions.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      try {
        if (timerRef.current) {
          clearInterval(timerRef.current)
        }
        mediaRecorderRef.current.stop()
        setIsRecording(false)
      } catch (error) {
        console.error('Error stopping recording:', error)
        toast({
          title: 'Error',
          description: 'Failed to stop recording.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }
  }

  const sendAudioForAnalysis = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'recording.webm')
      formData.append('session_type', sessionType)
      formData.append('topic', topic)

      // Get token from localStorage
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.')
      }

      // Use appropriate endpoint based on session type
      const endpoint = sessionType === 'enhanced' ? '/analyze-audio-enhanced' : '/analyze-audio'
      
      const response = await api.post<VoiceAnalysis>(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`,
        },
      })

      onAnalysisComplete(response.data)
      toast({
        title: 'Analysis Complete',
        description: sessionType === 'enhanced' 
          ? 'Enhanced analysis with language detection and AI voice detection completed.'
          : 'Your recording has been analyzed successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      const toastOptions = handleApiError(error)
      toast(toastOptions)
    } finally {
      setIsProcessing(false)
    }
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (hasPermission === false) {
    return (
      <Box p={4} bg={errorBg} borderRadius="md" border="1px solid" borderColor={borderColor}>
        <HStack spacing={2} color={errorColor}>
          <Icon as={FaExclamationTriangle} />
          <Text>Microphone access denied. Please enable microphone access in your browser settings.</Text>
        </HStack>
      </Box>
    )
  }

  return (
    <Box p={6} bg={bgColor} borderRadius="lg" boxShadow="md" maxW="400px" w="full" border="1px solid" borderColor={borderColor}>
      <VStack spacing={6} width="100%" p={4} bg={bgColor} borderRadius="lg" boxShadow="md">
              {hasPermission === false && (
                <Box 
                  p={4} 
                  bg={errorBg} 
                  color={errorColor} 
                  borderRadius="md" 
                  width="100%"
                  textAlign="center"
                >
                  <HStack justifyContent="center" spacing={2}>
                    <Icon as={FaExclamationTriangle} />
                    <Text>Microphone access is required for recording. Please enable it in your browser settings.</Text>
                  </HStack>
                </Box>
              )}

              <Box width="100%" textAlign="center">
                <Text fontSize="xl" fontWeight="bold" mb={2}>
                  {isRecording ? 'Recording...' : 'Ready to Record'}
                </Text>
                <Text fontSize="sm" color="gray.500" mb={4}>
                  {isRecording 
                    ? 'Speak clearly into your microphone' 
                    : 'Click the button below to start recording'}
                </Text>
              </Box>

              <Box width="100%" textAlign="center">
                {isRecording ? (
                  <Button
                    colorScheme="red"
                    leftIcon={<Icon as={FaStop} />}
                    onClick={stopRecording}
                    size="lg"
                    borderRadius="full"
                    px={8}
                    py={6}
                    boxShadow="lg"
                    _hover={{
                      transform: 'scale(1.05)',
                      boxShadow: 'xl',
                    }}
                    _active={{
                      transform: 'scale(0.95)',
                    }}
                    transition="all 0.2s"
                  >
                    Stop Recording
                  </Button>
                ) : (
                  <Button
                    colorScheme="blue"
                    leftIcon={<Icon as={FaMicrophone} />}
                    onClick={startRecording}
                    isDisabled={hasPermission === false}
                    size="lg"
                    borderRadius="full"
                    px={8}
                    py={6}
                    boxShadow="lg"
                    _hover={{
                      transform: 'scale(1.05)',
                      boxShadow: 'xl',
                    }}
                    _active={{
                      transform: 'scale(0.95)',
                    }}
                    transition="all 0.2s"
                  >
                    Start Recording
                  </Button>
                )}
              </Box>

              {isRecording && (
                <Box width="100%" mt={4}>
                  <HStack justify="space-between" mb={1}>
                    <Text fontSize="sm" color="gray.500">
                      {formatTime(recordingTime)}
                    </Text>
                    <Text fontSize="sm" color="gray.500">
                      Max: 5:00
                    </Text>
                  </HStack>
                  <Progress 
                    value={(recordingTime / 300) * 100} 
                    size="sm" 
                    colorScheme="blue" 
                    borderRadius="full"
                  />
                  <Box 
                    mt={2} 
                    height="4px" 
                    width={`${audioLevel}%`} 
                    bg="blue.400" 
                    borderRadius="full"
                    transition="width 0.1s"
                  />
                </Box>
              )}

              {lastAudioBlob && lastAudioUrl && (
                <Box width="100%" mt={4}>
                  <HStack spacing={4}>
                    <audio 
                      src={lastAudioUrl} 
                      controls 
                      style={{ flex: 1 }}
                    />
                    <Button 
                      as="a"
                      href={lastAudioUrl}
                      download={`recording-${new Date().toISOString()}.webm`}
                      leftIcon={<FaDownload />}
                      size="sm"
                      variant="outline"
                    >
                      Download
                    </Button>
                  </HStack>
                </Box>
              )}
      </VStack>
    </Box>
  )
}
