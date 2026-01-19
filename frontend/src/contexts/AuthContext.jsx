import { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mfaStatus, setMfaStatus] = useState(null);

  const fetchUser = async () => {
    try {
      // Use custom endpoint that includes role_bindings
      const response = await apiClient.get('/blockchain/user-info/');
      console.log('=== USER DATA ===', response.data);
      setUser(response.data);
      
      try {
        const mfaResponse = await apiClient.get('/authentication/mfa/status/');
        setMfaStatus(mfaResponse.data);
      } catch (err) {
        setMfaStatus({ mfa_verified: true, mfa_required: false });
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const isAdmin = () => {
    if (!user) return false;
    const result = user.is_superuser === true || 
           user.role_bindings?.some(rb => rb.role?.name === 'SystemAdmin');
    console.log('isAdmin result:', result);
    return result;
  };

  const value = {
    user,
    loading,
    mfaStatus,
    setMfaStatus,
    isAdmin,
    refetchUser: fetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
