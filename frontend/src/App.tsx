import React, { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useToast,
  Button,
  HStack,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  useDisclosure,
  useColorModeValue,
  Container,
  Flex,
  Badge,
  Icon,
  Spacer,
  Divider,
  useBreakpointValue,
  Fade,
  ScaleFade,
  SlideFade,
} from '@chakra-ui/react';
import { 
  FaChevronDown, 
  FaSignOutAlt, 
  FaCog, 
  FaMicrophone, 
  FaChartLine, 
  FaPlay, 
  FaDownload, 
  FaLanguage,
  FaCrown,
  FaRocket,
  FaStar,
  FaBrain,
  FaMagic,
  FaFire,
  FaGem
} from 'react-icons/fa';
import { AudioRecorder } from './components/AudioRecorder';
import { AnalysisDisplay } from './components/AnalysisDisplay';
import { ProgressDashboard } from './components/ProgressDashboard';
import { PracticeSession } from './components/PracticeSession';
import { EnhancedAnalysis } from './components/EnhancedAnalysis';
import { ComparisonCharts } from './components/ComparisonCharts';
import { DataExport } from './components/DataExport';
import { LanguageSettings } from './components/LanguageSettings';
import { LoginForm } from './components/LoginForm';
import { ThemeToggle } from './components/ThemeToggle';
import { Settings } from './components/Settings';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { VoiceAnalysis } from './types';
import { theme } from './theme';

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  return (
    <>
      <Menu>
        <MenuButton
          as={Button}
          rightIcon={<FaChevronDown />}
          leftIcon={<Avatar size="sm" name={user?.username} bg="purple.500" />}
          variant="ghost"
          colorScheme="purple"
          size="md"
          _hover={{ 
            bg: "purple.50", 
            transform: "translateY(-2px)",
            boxShadow: "0 8px 25px rgba(128, 90, 213, 0.15)"
          }}
          _active={{ transform: "translateY(0)" }}
          transition="all 0.2s"
        >
          <HStack spacing={2}>
            <Text fontWeight="600">{user?.username}</Text>
            <Badge colorScheme="purple" variant="subtle" fontSize="xs">
              Pro
            </Badge>
          </HStack>
        </MenuButton>
        <MenuList 
          bg="white" 
          border="1px solid" 
          borderColor="purple.100"
          boxShadow="0 20px 40px rgba(0,0,0,0.1)"
          borderRadius="xl"
          p={2}
        >
          <MenuItem 
            icon={<FaCog />} 
            onClick={onOpen}
            _hover={{ bg: "purple.50" }}
            borderRadius="lg"
            mb={1}
          >
            Settings
          </MenuItem>
          <Divider />
          <MenuItem 
            icon={<FaSignOutAlt />} 
            onClick={logout}
            _hover={{ bg: "red.50", color: "red.600" }}
            borderRadius="lg"
          >
            Logout
          </MenuItem>
        </MenuList>
      </Menu>
      <Settings isOpen={isOpen} onClose={onClose} />
    </>
  );
};

const MainContent: React.FC = () => {
  const [analysis, setAnalysis] = useState<VoiceAnalysis | null>(null);
  const { user, isAuthenticated } = useAuth();
  const toast = useToast();
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const textColor = useColorModeValue('gray.600', 'gray.300');
  const bgGradient = useColorModeValue(
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #232a47 0%, #22315a 100%)'
  );
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('purple.100', 'purple.700');

  const isMobile = useBreakpointValue({ base: true, md: false });

  const handleAnalysisComplete = (newAnalysis: VoiceAnalysis) => {
    setIsLoading(true);
    setAnalysis(newAnalysis);
    const currentSessions = Number(localStorage.getItem('totalSessions') || '0');
    localStorage.setItem('totalSessions', (currentSessions + 1).toString());

    setTimeout(() => {
      setIsLoading(false);
    toast({
        title: '🎉 Analysis Complete!',
      description: 'Your voice analysis is ready!',
      status: 'success',
        duration: 4000,
      isClosable: true,
        position: 'top-right',
    });
    }, 1000);
  };

  if (!isAuthenticated) {
    return (
      <Box minH="100vh" bgGradient={bgGradient} position="relative" overflow="hidden">
        {/* Animated Background Elements */}
        <Box
          position="absolute"
          top="10%"
          left="10%"
          w="200px"
          h="200px"
          bg="rgba(255,255,255,0.1)"
          borderRadius="full"
          className="float"
          animation="float 6s ease-in-out infinite"
        />
        <Box
          position="absolute"
          top="60%"
          right="15%"
          w="150px"
          h="150px"
          bg="rgba(255,255,255,0.05)"
          borderRadius="full"
          className="float"
          animation="float 8s ease-in-out infinite reverse"
        />
        <Box
          position="absolute"
          bottom="20%"
          left="20%"
          w="100px"
          h="100px"
          bg="rgba(255,255,255,0.08)"
          borderRadius="full"
          className="float"
          animation="float 4s ease-in-out infinite"
        />

        <Container maxW="container.lg" py={20} position="relative" zIndex={1}>
          <Fade in={true} delay={0.2}>
            <VStack spacing={12} textAlign="center">
              <ScaleFade in={true} delay={0.4}>
                <VStack spacing={4}>
                  <HStack spacing={3} align="center">
                    <Icon as={FaGem} boxSize={12} color="purple.300" />
                    <Heading 
                      size="4xl" 
                      bgGradient="linear(to-r, purple.400, pink.400)"
                      bgClip="text"
                      fontWeight="800"
                    >
            Vocal IQ
          </Heading>
                  </HStack>
                  <Text 
                    fontSize="2xl" 
                    color="white" 
                    fontWeight="300"
                    opacity={0.9}
                    maxW="600px"
                  >
            AI-Powered Voice Analytics for Smarter Learning
          </Text>
                  <HStack spacing={4} mt={4}>
                    <Badge colorScheme="purple" variant="solid" px={3} py={1} borderRadius="full">
                      <Icon as={FaBrain} mr={1} />
                      AI Analysis
                    </Badge>
                    <Badge colorScheme="pink" variant="solid" px={3} py={1} borderRadius="full">
                      <Icon as={FaRocket} mr={1} />
                      Real-time
                    </Badge>
                    <Badge colorScheme="blue" variant="solid" px={3} py={1} borderRadius="full">
                      <Icon as={FaStar} mr={1} />
                      Premium
                    </Badge>
                  </HStack>
                </VStack>
              </ScaleFade>

              <SlideFade in={true} delay={0.6} offsetY={20}>
                <Box
                  bg={cardBg}
                  p={8}
                  borderRadius="2xl"
                  boxShadow="0 25px 50px rgba(0,0,0,0.15)"
                  border="1px solid"
                  borderColor={borderColor}
                  backdropFilter="blur(10px)"
                  maxW="500px"
                  w="full"
                >
          <LoginForm />
                </Box>
              </SlideFade>
        </VStack>
          </Fade>
        </Container>
      </Box>
    );
  }

  return (
    <Box minH="100vh" bgGradient={bgGradient} position="relative">
      {/* Animated Background Elements */}
      <Box
        position="absolute"
        top="5%"
        right="5%"
        w="100px"
        h="100px"
        bg="rgba(255,255,255,0.1)"
        borderRadius="full"
        className="float"
        animation="float 5s ease-in-out infinite"
      />
      <Box
        position="absolute"
        bottom="10%"
        left="5%"
        w="80px"
        h="80px"
        bg="rgba(255,255,255,0.05)"
        borderRadius="full"
        className="float"
        animation="float 7s ease-in-out infinite reverse"
      />

      <Container maxW="container.xl" py={8} position="relative" zIndex={1}>
        <Fade in={true}>
          <VStack spacing={8}>
            {/* Header */}
            <Flex 
              w="full" 
              justify="space-between" 
              align="center"
              bg={cardBg}
              p={6}
              borderRadius="2xl"
              boxShadow="0 10px 30px rgba(0,0,0,0.1)"
              border="1px solid"
              borderColor={borderColor}
              backdropFilter="blur(10px)"
            >
              <HStack spacing={4}>
                <Icon as={FaGem} boxSize={8} color="purple.500" />
                <VStack align="start" spacing={0}>
                  <Heading size="xl" bgGradient="linear(to-r, purple.500, pink.500)" bgClip="text">
            Vocal IQ
          </Heading>
                  <Text fontSize="sm" color={textColor}>
                    AI Voice Analytics Platform
                  </Text>
                </VStack>
              </HStack>
          <HStack spacing={4}>
            <ThemeToggle />
            <UserMenu />
          </HStack>
            </Flex>

            {/* Welcome Message */}
            <ScaleFade in={true} delay={0.2}>
              <Box
                bg={cardBg}
                p={6}
                borderRadius="xl"
                boxShadow="0 8px 25px rgba(0,0,0,0.1)"
                border="1px solid"
                borderColor={borderColor}
                textAlign="center"
                maxW="600px"
                w="full"
              >
                <HStack justify="center" mb={3}>
                  <Icon as={FaFire} color="orange.500" boxSize={5} />
                  <Text fontSize="lg" fontWeight="600" color={textColor}>
                    Welcome back, {user?.username}!
                  </Text>
        </HStack>
                <Text fontSize="md" color={textColor} opacity={0.8}>
                  Ready to improve your speaking skills with AI-powered analytics?
        </Text>
              </Box>
            </ScaleFade>

            {/* Main Tabs */}
            <Box w="full" bg={cardBg} borderRadius="2xl" boxShadow="0 15px 35px rgba(0,0,0,0.1)" border="1px solid" borderColor={borderColor} overflow="hidden">
        <Tabs 
                variant="enclosed" 
          colorScheme="purple" 
          w="full" 
          index={activeTab}
          onChange={setActiveTab}
        >
                <TabList 
                  bg="gray.50" 
                  borderBottom="1px solid" 
                  borderColor="gray.200"
                  flexWrap="wrap"
                  justifyContent="center"
                  p={2}
                >
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaMicrophone} />
                      <Text display={isMobile ? "none" : "block"}>Quick Analysis</Text>
                    </HStack>
                  </Tab>
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaBrain} />
                      <Text display={isMobile ? "none" : "block"}>Enhanced Analysis</Text>
                    </HStack>
                  </Tab>
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaPlay} />
                      <Text display={isMobile ? "none" : "block"}>Practice Session</Text>
                    </HStack>
                  </Tab>
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaChartLine} />
                      <Text display={isMobile ? "none" : "block"}>Charts</Text>
                    </HStack>
                  </Tab>
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaCrown} />
                      <Text display={isMobile ? "none" : "block"}>Dashboard</Text>
                    </HStack>
                  </Tab>
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaDownload} />
                      <Text display={isMobile ? "none" : "block"}>Export</Text>
                    </HStack>
                  </Tab>
                  <Tab 
                    _selected={{ 
                      bg: "purple.500", 
                      color: "white",
                      transform: "translateY(-2px)",
                      boxShadow: "0 4px 12px rgba(128, 90, 213, 0.3)"
                    }}
                    _hover={{ bg: "purple.100" }}
                    transition="all 0.2s"
                    borderRadius="lg"
                    mx={1}
                    mb={2}
                  >
                    <HStack spacing={2}>
                      <Icon as={FaLanguage} />
                      <Text display={isMobile ? "none" : "block"}>Languages</Text>
                    </HStack>
                  </Tab>
          </TabList>

                <TabPanels p={6}>
            <TabPanel>
                    <Fade in={activeTab === 0} delay={0.1}>
              <VStack spacing={8} w="full">
                <Box w="full" maxW="600px" mx="auto">
                  <AudioRecorder
                    onAnalysisComplete={handleAnalysisComplete}
                    sessionType="quick"
                    topic="general"
                  />
                </Box>
                        {analysis && (
                          <ScaleFade in={!!analysis} delay={0.2}>
                            <AnalysisDisplay analysis={analysis} />
                          </ScaleFade>
                        )}
              </VStack>
                    </Fade>
            </TabPanel>

            <TabPanel>
                    <Fade in={activeTab === 1} delay={0.1}>
              <VStack spacing={8} w="full">
                <Box w="full" maxW="600px" mx="auto">
                  <AudioRecorder
                    onAnalysisComplete={handleAnalysisComplete}
                    sessionType="enhanced"
                    topic="general"
                  />
                </Box>
                        {analysis && (
                          <ScaleFade in={!!analysis} delay={0.2}>
                            <EnhancedAnalysis analysis={analysis} />
                          </ScaleFade>
                        )}
              </VStack>
                    </Fade>
            </TabPanel>

            <TabPanel>
                    <Fade in={activeTab === 2} delay={0.1}>
              <PracticeSession onAnalysisComplete={handleAnalysisComplete} />
                    </Fade>
            </TabPanel>

            <TabPanel>
                    <Fade in={activeTab === 3} delay={0.1}>
              <ComparisonCharts />
                    </Fade>
            </TabPanel>

            <TabPanel>
                    <Fade in={activeTab === 4} delay={0.1}>
              <ProgressDashboard />
                    </Fade>
            </TabPanel>

            <TabPanel>
                    <Fade in={activeTab === 5} delay={0.1}>
              <DataExport />
                    </Fade>
            </TabPanel>

            <TabPanel>
                    <Fade in={activeTab === 6} delay={0.1}>
              <LanguageSettings />
                    </Fade>
            </TabPanel>
          </TabPanels>
        </Tabs>
            </Box>
      </VStack>
        </Fade>
      </Container>
    </Box>
  );
};

const App: React.FC = () => {
  return (
    <ChakraProvider theme={theme}>
      <ThemeProvider>
        <AuthProvider>
          <MainContent />
        </AuthProvider>
      </ThemeProvider>
    </ChakraProvider>
  );
};

export default App;


