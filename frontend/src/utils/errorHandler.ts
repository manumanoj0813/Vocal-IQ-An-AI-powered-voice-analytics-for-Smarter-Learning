import { UseToastOptions } from '@chakra-ui/react';

export const handleApiError = (error: any): UseToastOptions => {
  console.error('API Error:', error);

  if (error.response) {
    const { status, data } = error.response;

    switch (status) {
      case 401:
        // Unauthorized - handle different login error scenarios
        console.error('Authentication error:', data);
        
        // Check for specific login error messages from backend
        const loginErrorMessage = data?.detail?.toLowerCase() || '';
        
        if (loginErrorMessage.includes('invalid credentials')) {
          return {
            title: 'Login Failed',
            description: 'Invalid email or password. Please try again.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          };
        } else if (loginErrorMessage.includes('account locked')) {
          return {
            title: 'Account Locked',
            description: 'Your account has been locked. Please contact support.',
            status: 'error',
            duration: 7000,
            isClosable: true,
          };
        } else if (loginErrorMessage.includes('expired')) {
          localStorage.removeItem('token');
          window.location.href = '/';
          return {
            title: 'Session Expired',
            description: 'Your session has expired. Please log in again.',
            status: 'warning',
            duration: 5000,
            isClosable: true,
          };
        }
        
        // Default unauthorized error
        localStorage.removeItem('token');
        return {
          title: 'Authentication Error',
          description: 'Please check your credentials and try again.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        };

      case 403:
        console.error('Access forbidden:', data);
        return {
          title: 'Access Denied',
          description: 'You do not have permission to perform this action.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        };

      case 404:
        console.error('Not Found:', data);
        return {
          title: 'Error: Not Found',
          description: `The requested resource was not found on the server. Endpoint: ${error.config.url}`,
          status: 'error',
          duration: 7000,
          isClosable: true,
        };

      case 500:
        console.error('Server error:', data);
        return {
          title: 'Server Error',
          description: 'An unexpected error occurred. Please try again later.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        };

      default:
        console.error('Request failed:', data);
        return {
          title: 'Error',
          description: data?.detail || 'An error occurred. Please try again.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        };
    }
  } else if (error.request) {
    // Request was made but no response received
    console.error('No response received:', error.request);
    return {
      title: 'Connection Error',
      description: 'Could not connect to the server. Please check your internet connection.',
      status: 'error',
      duration: 5000,
      isClosable: true,
    };
  } else {
    // Something happened in setting up the request
    console.error('Error setting up request:', error.message);
    return {
      title: 'Request Error',
      description: 'Failed to send request. Please try again.',
      status: 'error',
      duration: 5000,
      isClosable: true,
    };
  }
}; 