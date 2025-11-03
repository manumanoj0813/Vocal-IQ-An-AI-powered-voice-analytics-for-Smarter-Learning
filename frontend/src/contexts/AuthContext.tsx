import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { AuthResponse, User, LoginCredentials, RegisterData } from '../types';
import api from '../config/api';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  getAccessToken: () => Promise<string | null>;
}

interface JwtPayload {
  exp: number;
  sub: string;
  [key: string]: any;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.exp * 1000 < Date.now();
  } catch (error) {
    return true;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const refreshToken = useCallback(async (): Promise<string | null> => {
    if (isRefreshing) return null;
    
    setIsRefreshing(true);
    try {
      const response = await api.post<{ access_token: string }>('/token/refresh');
      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('token', access_token);
        return access_token;
      }
      return null;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      logout();
      return null;
    } finally {
      setIsRefreshing(false);
    }
  }, [isRefreshing, logout]);

  const fetchUserData = useCallback(async (token: string) => {
    try {
      console.log('Fetching user data with token:', token.substring(0, 10) + '...');
      
      // First try /users/me endpoint
      try {
        const response = await api.get<User>('/users/me', {
          headers: {
            Authorization: `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });
        
        console.log('User data response from /users/me:', response.data);
        if (response.data) {
          setUser(response.data);
          setIsAuthenticated(true);
          return true;
        }
      } catch (meError) {
        console.log('Failed to fetch from /users/me, trying /auth/me...', meError);
        
        // Fall back to /auth/me if /users/me fails
        const authResponse = await api.get<User>('/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
            'Accept': 'application/json'
          }
        });
        
        console.log('User data response from /auth/me:', authResponse.data);
        if (authResponse.data) {
          setUser(authResponse.data);
          setIsAuthenticated(true);
          return true;
        }
      }
      
      // If we get here, neither endpoint worked
      throw new Error('Failed to fetch user data from any endpoint');
    } catch (error: any) {
      console.error('Error fetching user data:', error);
      
      // If the token is invalid or expired, try to refresh it
      if (error.response?.status === 401) {
        console.log('Token might be expired, attempting to refresh...');
        const newToken = await refreshToken();
        if (newToken) {
          return fetchUserData(newToken);
        }
      }
      
      // Only logout if we're not already refreshing the token
      if (!isRefreshing) {
        console.log('Logging out due to error');
        logout();
      }
      
      throw error; // Re-throw to be handled by the caller
    }
  }, [isRefreshing, logout, refreshToken]);

  const getAccessToken = useCallback(async (): Promise<string | null> => {
    let token = localStorage.getItem('token');
    
    if (!token) {
      return null;
    }

    if (isTokenExpired(token)) {
      if (isRefreshing) {
        // If already refreshing, wait for it to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        return localStorage.getItem('token');
      }
      
      setIsRefreshing(true);
      try {
        const newToken = await refreshToken();
        setIsRefreshing(false);
        return newToken;
      } catch (error) {
        setIsRefreshing(false);
        return null;
      }
    }
    
    return token;
  }, [isRefreshing, refreshToken]);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        console.log('Initial auth check, token exists:', !!token);
        
        if (token) {
          if (!isTokenExpired(token)) {
            console.log('Token is valid, fetching user data...');
            const success = await fetchUserData(token);
            if (!success) {
              console.log('Failed to fetch user data, clearing token');
              localStorage.removeItem('token');
              setUser(null);
              setIsAuthenticated(false);
            }
          } else {
            console.log('Token expired, attempting to refresh...');
            const newToken = await refreshToken();
            if (newToken) {
              await fetchUserData(newToken);
            } else {
              console.log('Failed to refresh token, logging out');
              localStorage.removeItem('token');
              setUser(null);
              setIsAuthenticated(false);
            }
          }
        } else {
          console.log('No token found, user is not authenticated');
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        localStorage.removeItem('token');
        setUser(null);
        setIsAuthenticated(false);
      }
    };

    initializeAuth();
  }, [fetchUserData, refreshToken]);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      console.log('Attempting login with credentials:', credentials.username);
      
      // Try the OAuth2 token endpoint first
      try {
        const params = new URLSearchParams();
        params.append('username', credentials.username);
        params.append('password', credentials.password);
        params.append('grant_type', 'password');
        
        const response = await api.post<{ access_token: string }>('/token', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
          }
        });
        
        if (response.data?.access_token) {
          const { access_token } = response.data;
          localStorage.setItem('token', access_token);
          await fetchUserData(access_token);
          return;
        }
      } catch (tokenError) {
        console.log('OAuth2 token endpoint failed, trying direct login...', tokenError);
      }
      
      // Fall back to direct login if OAuth2 fails
      const response = await api.post<{ access_token: string }>('/auth/login', {
        username: credentials.username,
        password: credentials.password
      });
      
      console.log('Login response:', response.data);
      
      if (response.data?.access_token) {
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        await fetchUserData(access_token);
      } else {
        throw new Error('No access token received');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      let errorMessage = 'Failed to login';
      
      if (error.response) {
        // Handle HTTP error responses
        errorMessage = error.response.data?.detail || 
                      error.response.data?.message || 
                      `Server responded with ${error.response.status}`;
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something happened in setting up the request
        errorMessage = error.message || 'An unknown error occurred';
      }
      
      throw new Error(errorMessage);
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    try {
      // Make sure the endpoint matches your backend API
      const response = await api.post<AuthResponse>('/auth/register', {
        username: data.username,
        email: data.email,
        password: data.password
      });

      if (response.data?.access_token) {
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        await fetchUserData(access_token);
        return; // Successfully registered and logged in
      } else {
        throw new Error('No access token received');
      }
    } catch (error: any) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.message || 
                         'Registration failed';
      throw new Error(errorMessage);
    }
  };

  // logout function is already defined at the top of the component

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      login, 
      register, 
      logout,
      getAccessToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};