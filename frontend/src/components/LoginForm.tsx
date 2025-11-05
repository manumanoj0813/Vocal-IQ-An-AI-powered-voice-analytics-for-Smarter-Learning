import React, { useState } from 'react';
import {
  Box,
  VStack,
  FormControl,
  FormLabel,
  Input,
  Button,
  Text,
  useToast,
  Heading,
  Divider,
  useColorModeValue,
  HStack,
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import { LoginCredentials, RegisterData } from '../types';
import api from '../config/api';

export const LoginForm: React.FC = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [formData, setFormData] = useState<RegisterData>({
    username: '',
    password: '',
    email: '',
  });
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isResetMode, setIsResetMode] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const { login } = useAuth();
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isRegistering) {
        if (!formData.email) throw new Error('Email is required for registration');
        const res = await api.post('/auth/register', { ...formData });
        const data = res.data as any;
        localStorage.setItem('token', data.access_token);
        window.location.reload();
        toast({ title: 'Registration Successful', status: 'success' });
      } else if (isResetMode) {
        const res = await api.post('/auth/reset-password', { token: resetToken, new_password: newPassword });
        toast({ title: 'Password reset', status: 'success' });
        setIsResetMode(false);
      } else {
        const res = await api.post('/login', { username: formData.username, password: formData.password });
        const data = res.data as any;
        localStorage.setItem('token', data.access_token);
        window.location.reload();
        toast({ title: 'Login Successful', description: 'Welcome back!', status: 'success', duration: 5000, isClosable: true });
      }
    } catch (error) {
      toast({ title: 'Error', description: error instanceof Error ? error.message : 'Operation failed', status: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // OTP flow removed

  // Registration OTP flow removed

  const sendReset = async () => {
    try {
      if (!resetEmail) throw new Error('Enter your email');
      await api.post('/auth/forgot-password', { email: resetEmail });
      toast({ title: 'Reset email sent', description: 'Check your inbox', status: 'success' });
    } catch (e) {
      toast({ title: 'Error', description: e instanceof Error ? e.message : 'Failed to request reset', status: 'error' });
    }
  };

  return (
    <Box w="full" maxW="400px" p={6} bg={bgColor} borderRadius="lg" boxShadow="md" border="1px solid" borderColor={borderColor}>
      <VStack spacing={6} as="form" onSubmit={handleSubmit}>
        <Heading size="lg" color="purple.600">
          {isRegistering ? 'Create Account' : isResetMode ? 'Reset Password' : 'Welcome Back'}
        </Heading>

        {!isResetMode && (
          <>
            <FormControl isRequired>
              <FormLabel>Username</FormLabel>
              <Input name="username" value={formData.username} onChange={handleInputChange} placeholder="Enter your username" />
            </FormControl>

            {isRegistering && (
              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input name="email" type="email" value={formData.email} onChange={handleInputChange} placeholder="Enter your email" />
              </FormControl>
            )}

            <FormControl isRequired>
              <FormLabel>Password</FormLabel>
              <Input name="password" type="password" value={formData.password} onChange={handleInputChange} placeholder="Enter your password" />
            </FormControl>

            {/* OTP inputs removed for simplified login */}

            {/* Registration OTP removed */}
          </>
        )}

        {isResetMode && (
          <>
            <FormControl isRequired>
              <FormLabel>Email</FormLabel>
              <HStack>
                <Input value={resetEmail} onChange={(e) => setResetEmail(e.target.value)} placeholder="you@example.com" />
                <Button onClick={sendReset} variant="outline">Send Reset</Button>
              </HStack>
            </FormControl>
            <FormControl isRequired>
              <FormLabel>Reset Token</FormLabel>
              <Input value={resetToken} onChange={(e) => setResetToken(e.target.value)} placeholder="Paste token" />
            </FormControl>
            <FormControl isRequired>
              <FormLabel>New Password</FormLabel>
              <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Enter new password" />
            </FormControl>
          </>
        )}

        <Button type="submit" colorScheme="purple" size="lg" w="full" isLoading={isLoading}>
          {isRegistering ? 'Register' : isResetMode ? 'Reset Password' : 'Login'}
        </Button>

        <Divider />

        {!isResetMode && (
          <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
            {isRegistering ? 'Already have an account?' : "Don't have an account?"}
            <Button variant="link" colorScheme="purple" ml={2} onClick={() => setIsRegistering(!isRegistering)}>
              {isRegistering ? 'Login' : 'Register'}
            </Button>
          </Text>
        )}

        <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
          {isResetMode ? 'Remembered your password?' : 'Forgot password?'}
          <Button variant="link" colorScheme="purple" ml={2} onClick={() => setIsResetMode(!isResetMode)}>
            {isResetMode ? 'Back to Login' : 'Reset here'}
          </Button>
        </Text>
      </VStack>
    </Box>
  );
};


