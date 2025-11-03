
import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  FormControl,
  FormLabel,
  Switch,
  Select,
  Avatar,
  Box,
  Divider,
  useToast,
  useColorModeValue,
  Badge,
  Icon,
} from '@chakra-ui/react';
import { FaUser, FaBell, FaSave, FaTimes, FaCog } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');

  // Profile settings
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    fullName: '',
    bio: '',
  });

  // Preferences
  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    pushNotifications: false,
    autoSave: true,
    soundEffects: true,
    theme: 'auto',
    language: 'en',
    analysisQuality: 'high',
  });

  const handleProfileSave = () => {
    // Here you would typically save to backend
    toast({
      title: 'Profile Updated',
      description: 'Your profile has been saved successfully.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const handlePreferencesSave = () => {
    // Here you would typically save to backend
    toast({
      title: 'Preferences Saved',
      description: 'Your preferences have been updated.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const handleResetSettings = () => {
    setPreferences({
      emailNotifications: true,
      pushNotifications: false,
      autoSave: true,
      soundEffects: true,
      theme: 'auto',
      language: 'en',
      analysisQuality: 'high',
    });
    toast({
      title: 'Settings Reset',
      description: 'Settings have been reset to default values.',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent bg={bgColor}>
        <ModalHeader>
          <HStack>
            <Icon as={FaCog} color="purple.500" />
            <Text>Settings</Text>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <VStack spacing={6} align="stretch">
            {/* Profile Section */}
            <Box>
              <HStack mb={4}>
                <Icon as={FaUser} color="purple.500" />
                <Text fontSize="lg" fontWeight="semibold">Profile Settings</Text>
              </HStack>
              
              <VStack spacing={4} align="stretch">
                <HStack spacing={4}>
                  <Avatar size="lg" name={profileData.username} />
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">{profileData.username}</Text>
                    <Badge colorScheme="purple">Premium User</Badge>
                  </VStack>
                </HStack>

                <FormControl>
                  <FormLabel>Username</FormLabel>
                  <Input
                    value={profileData.username}
                    onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                    placeholder="Enter username"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Email</FormLabel>
                  <Input
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                    placeholder="Enter email"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Full Name</FormLabel>
                  <Input
                    value={profileData.fullName}
                    onChange={(e) => setProfileData({...profileData, fullName: e.target.value})}
                    placeholder="Enter full name"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Bio</FormLabel>
                  <Input
                    value={profileData.bio}
                    onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                    placeholder="Tell us about yourself"
                  />
                </FormControl>

                <Button leftIcon={<FaSave />} colorScheme="purple" onClick={handleProfileSave}>
                  Save Profile
                </Button>
              </VStack>
            </Box>

            <Divider />

            {/* Preferences Section */}
            <Box>
              <HStack mb={4}>
                <Icon as={FaBell} color="purple.500" />
                <Text fontSize="lg" fontWeight="semibold">Preferences</Text>
              </HStack>

              <VStack spacing={4} align="stretch">
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Email Notifications</FormLabel>
                  <Switch
                    isChecked={preferences.emailNotifications}
                    onChange={(e) => setPreferences({...preferences, emailNotifications: e.target.checked})}
                  />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Push Notifications</FormLabel>
                  <Switch
                    isChecked={preferences.pushNotifications}
                    onChange={(e) => setPreferences({...preferences, pushNotifications: e.target.checked})}
                  />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Auto-save Sessions</FormLabel>
                  <Switch
                    isChecked={preferences.autoSave}
                    onChange={(e) => setPreferences({...preferences, autoSave: e.target.checked})}
                  />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Sound Effects</FormLabel>
                  <Switch
                    isChecked={preferences.soundEffects}
                    onChange={(e) => setPreferences({...preferences, soundEffects: e.target.checked})}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Theme</FormLabel>
                  <Select
                    value={preferences.theme}
                    onChange={(e) => setPreferences({...preferences, theme: e.target.value})}
                  >
                    <option value="auto">Auto (System)</option>
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Language</FormLabel>
                  <Select
                    value={preferences.language}
                    onChange={(e) => setPreferences({...preferences, language: e.target.value})}
                  >
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                    <option value="kn">Kannada</option>
                    <option value="te">Telugu</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Analysis Quality</FormLabel>
                  <Select
                    value={preferences.analysisQuality}
                    onChange={(e) => setPreferences({...preferences, analysisQuality: e.target.value})}
                  >
                    <option value="low">Low (Faster)</option>
                    <option value="medium">Medium</option>
                    <option value="high">High (Slower)</option>
                  </Select>
                </FormControl>

                <HStack spacing={3}>
                  <Button leftIcon={<FaSave />} colorScheme="purple" onClick={handlePreferencesSave}>
                    Save Preferences
                  </Button>
                  <Button leftIcon={<FaTimes />} variant="outline" onClick={handleResetSettings}>
                    Reset to Default
                  </Button>
                </HStack>
              </VStack>
            </Box>

            <Divider />

            {/* Account Actions */}
            <Box>
              <Text fontSize="lg" fontWeight="semibold" mb={4}>Account Actions</Text>
              <VStack spacing={3} align="stretch">
                <Button variant="outline" colorScheme="red" onClick={logout}>
                  Sign Out
                </Button>
                <Text fontSize="sm" color="gray.500">
                  Version 1.0.0 • Last updated: {new Date().toLocaleDateString()}
                </Text>
              </VStack>
            </Box>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
}; 