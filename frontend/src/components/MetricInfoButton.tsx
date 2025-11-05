import React from 'react'
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  useDisclosure,
  VStack,
  Text,
  HStack,
} from '@chakra-ui/react'
import { Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, Box, Badge } from '@chakra-ui/react'
import api from '../config/api'

type Props = { analysis?: any }

export const MetricInfoButton: React.FC<Props> = ({ analysis }) => {
  const { isOpen, onOpen, onClose } = useDisclosure()

  const am = analysis?.audio_metrics || {}
  const clarity = am?.clarity || {}
  const rhythm = am?.rhythm || {}
  const pitch = am?.pitch || {}
  const emotion = am?.emotion || {}
  const fluency = am?.fluency || {}

  const downloadExplanationsPdf = async () => {
    try {
      const payload = { ...(analysis || {}), _include_explanations: true }
      const res = await api.post('/export-analysis-pdf', payload, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = 'vocal_iq_explanations.pdf'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      // silent fail in modal
    }
  }

  return (
    <>
      <HStack>
        <Button size="sm" variant="outline" onClick={onOpen}>What do these scores mean?</Button>
        <Button size="sm" variant="outline" onClick={downloadExplanationsPdf}>Download as PDF</Button>
      </HStack>
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>What your scores mean</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack align="start" spacing={3} fontSize="sm">
              <Text>We listen to tiny slices of your audio and measure simple patterns. Open a section to see what the score means and your numbers.</Text>
              <Accordion allowToggle w="full">
                {/* 1. Pitch Analysis */}
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex='1' textAlign='left' fontWeight="semibold">1. Pitch Analysis</Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={2}>
                      <Text>How high or low your voice is, and how smoothly it moves.</Text>
                      <Box pl={4}>
                        <Text>• (i) Average Pitch: typical note of your voice (Hz){typeof pitch?.average_pitch === 'number' && ` — ${Math.round(pitch.average_pitch)} Hz`}</Text>
                        <Text>• (ii) Stability: how steady your pitch stays{typeof pitch?.pitch_stability === 'number' && ` — ${(pitch.pitch_stability*100).toFixed(1)}%`}</Text>
                        <Text>• (iii) Contour Score: smoothness of your pitch shape{typeof pitch?.pitch_contour === 'number' && ` — ${(pitch.pitch_contour*100).toFixed(1)}%`}</Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>

                {/* 2. Rhythm Analysis */}
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex='1' textAlign='left' fontWeight="semibold">2. Rhythm Analysis</Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={2}>
                      <Text>Your pace and pauses.</Text>
                      <Box pl={4}>
                        <Text>• Speech Rate: how fast you speak{typeof rhythm?.speech_rate === 'number' && ` — ${(rhythm.speech_rate*100).toFixed(1)}%`}</Text>
                        <Text>• (i) Pause Ratio: how much silence you leave{typeof rhythm?.pause_ratio === 'number' && ` — ${(rhythm.pause_ratio*100).toFixed(1)}%`}</Text>
                        <Text>• (ii) Consistency: how steady your rhythm is{typeof rhythm?.rhythm_consistency === 'number' && ` — ${(rhythm.rhythm_consistency*100).toFixed(1)}%`}</Text>
                        <Text>• (iii) Stress Pattern: overall feel (dynamic/flat){typeof rhythm?.stress_pattern === 'string' && rhythm.stress_pattern && ` — ${rhythm.stress_pattern}`}</Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>

                {/* 3. Clarity Analysis */}
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex='1' textAlign='left' fontWeight="semibold">3. Clarity Analysis</Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={2}>
                      <Text>How easy it is to understand you.</Text>
                      <Box pl={4}>
                        <Text>• (i) Overall Clarity: general clearness{typeof clarity?.clarity_score === 'number' && ` — ${(clarity.clarity_score*100).toFixed(1)}%`}</Text>
                        <Text>• (ii) Enunciation: how crisply you pronounce words{typeof clarity?.enunciation_quality === 'number' && ` — ${(clarity.enunciation_quality*100).toFixed(1)}%`}</Text>
                        <Text>• (iii) Projection: speaking loud and clear enough{typeof clarity?.voice_projection === 'number' && ` — ${(clarity.voice_projection*100).toFixed(1)}%`}</Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>

                {/* 4. Emotion Analysis */}
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex='1' textAlign='left' fontWeight="semibold">4. Emotion Analysis</Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={2}>
                      <Text>Your main emotion and how sure/steady it is.</Text>
                      <Box pl={4}>
                        <Text>• (i) Dominant Emotion: the emotion your voice sounds most like.</Text>
                        <Text>• (ii) Confidence: how sure we are about that emotion.</Text>
                        <Text>• (iii) Range: how much your emotion changed (wide vs flat).</Text>
                        <Text>• (iv) Stability: how steady your emotion stayed (less jumping).</Text>
                      </Box>
                      <Box pl={4}>
                        <Text>• (i) Dominant Emotion{typeof emotion?.dominant_emotion === 'string' && ` — ${emotion.dominant_emotion}`}</Text>
                        <Text>• (ii) Confidence{typeof emotion?.emotion_confidence === 'number' && ` — ${(emotion.emotion_confidence*100).toFixed(1)}%`}</Text>
                        <Text>• (iii) Range{typeof emotion?.emotional_range === 'string' && ` — ${emotion.emotional_range}`}</Text>
                        <Text>• (iv) Stability{typeof emotion?.emotional_stability === 'number' && ` — ${(emotion.emotional_stability*100).toFixed(1)}%`}</Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>

                {/* 5. Fluency Analysis */}
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex='1' textAlign='left' fontWeight="semibold">5. Fluency Analysis</Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={2}>
                      <Text>Flow of your speech.</Text>
                      <Box pl={4}>
                        <Text>• (i) Fluency Score: overall smooth flow while speaking.</Text>
                        <Text>• (ii) Smoothness: how even your speech sounds (fewer bumps).</Text>
                        <Text>• (iii) Hesitations: um/uh pauses or long stops (lower is better).</Text>
                        <Text>• (iv) Repetitions: repeated words/phrases (lower is better).</Text>
                      </Box>
                      <Box pl={4}>
                        <Text>• (i) Fluency Score — overall fluency rating{typeof fluency?.fluency_score === 'number' && ` — ${(fluency.fluency_score*100).toFixed(1)}%`}</Text>
                        <Text>• (ii) Smoothness{typeof fluency?.smoothness === 'number' && ` — ${(fluency.smoothness*100).toFixed(1)}%`}</Text>
                        <Text>• (iii) Hesitations{typeof fluency?.hesitations === 'number' && ` — ${(fluency.hesitations*100).toFixed(1)}%`}</Text>
                        <Text>• (iv) Repetitions{typeof fluency?.repetitions === 'number' && ` — ${(fluency.repetitions*100).toFixed(1)}%`}</Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>

                {/* 6. Transcription */}
                <AccordionItem>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex='1' textAlign='left' fontWeight="semibold">6. Transcription</Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={2}>
                      <Text>Words we heard and how sure we are.</Text>
                      <Box pl={4}>
                        <Text>• (i) Word Count{typeof analysis?.transcription?.word_count === 'number' && ` — ${analysis.transcription.word_count}`}</Text>
                        <Text>• (ii) Confidence{typeof analysis?.transcription?.transcription_confidence === 'number' && ` — ${(analysis.transcription.transcription_confidence*100).toFixed(1)}%`}</Text>
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              </Accordion>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}

export default MetricInfoButton


