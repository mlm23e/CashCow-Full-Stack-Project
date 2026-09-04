/**
 * CashCow
 * global Auth state using React's context API
 */

import { createContext, useContext, useMemo, useState } from 'react';
import apiClient from '../api/client.js';

const AuthContext = createContext(null);

function decodeToken(token) {
  if (!token) {
    return null;
  }

  try {
    const payloadSegment = token.split('.')[1];
    const decoded = JSON.parse(atob(payloadSegment));
    return {
      username: decoded.sub,
      role: decoded.role,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('CashCowToken'));

  const user = useMemo(() => (token ? decodeToken(token) : null), [token]);

  const login = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const accessToken = response.data.access_token;
    localStorage.setItem('CashCowToken', accessToken);
    setToken(accessToken);
  };

  const logout = () => {
    localStorage.removeItem('CashCowToken');
    setToken(null);
  };

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}