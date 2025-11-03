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
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import { LoginCredentials, RegisterData } from '../types';

export const LoginForm: React.FC = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [formData, setFormData] = useState<RegisterData>({
    username: '',
    password: '',
    email: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isRegistering) {
        if (!formData.email) {
          throw new Error('Email is required for registration');
        }
        await register(formData);
        toast({
          title: 'Registration Successful',
          description: 'Welcome to Vocal IQ!',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      } else {
        const loginData: LoginCredentials = {
          username: formData.username,
          password: formData.password,
        };
        await login(loginData);
        toast({
          title: 'Login Successful',
          description: 'Welcome back!',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Authentication failed',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <Box
      w="full"
      maxW="400px"
      p={6}
      bg={bgColor}
      borderRadius="lg"
      boxShadow="md"
      border="1px solid"
      borderColor={borderColor}
    >
      <VStack spacing={6} as="form" onSubmit={handleSubmit}>
        <Heading size="lg" color="purple.600">
          {isRegistering ? 'Create Account' : 'Welcome Back'}
        </Heading>

        <FormControl isRequired>
          <FormLabel>Username</FormLabel>
          <Input
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            placeholder="Enter your username"
          />
        </FormControl>

        {isRegistering && (
          <FormControl isRequired>
            <FormLabel>Email</FormLabel>
            <Input
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter your email"
            />
          </FormControl>
        )}

        <FormControl isRequired>
          <FormLabel>Password</FormLabel>
          <Input
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            placeholder="Enter your password"
          />
        </FormControl>

        <Button
          type="submit"
          colorScheme="purple"
          size="lg"
          w="full"
          isLoading={isLoading}
        >
          {isRegistering ? 'Register' : 'Login'}
        </Button>

        <Divider />

        <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
          {isRegistering ? 'Already have an account?' : "Don't have an account?"}
          <Button
            variant="link"
            colorScheme="purple"
            ml={2}
            onClick={() => setIsRegistering(!isRegistering)}
          >
            {isRegistering ? 'Login' : 'Register'}
          </Button>
        </Text>
      </VStack>
    </Box>
  );
};


