#!/bin/bash

set -e

FRONTEND_DIR=~/Desktop/truefypjs/frontend

echo "[1] Patching api.js (adding Bearer token header)..."

cat > $FRONTEND_DIR/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Automatically attach Bearer token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;

export const userAPI = {
  me: () => apiClient.get('/users/users/me/'),
};
EOF

echo "[2] Patching Login.jsx to store token..."

cat > $FRONTEND_DIR/src/pages/Login.jsx << 'EOF'
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/api';
import Button from '../components/common/Button';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Request token from Django
      const response = await apiClient.post('/authentication/tokens/', {
        username,
        password,
      });

      // Save token locally
      localStorage.setItem('auth_token', response.data.token);

      // Redirect directly (skip MFA for now)
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please check your credentials.');
      setPassword('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            JumpServer Blockchain
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Chain of Custody System
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <input
              id="username"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="block w-full px-3 py-2 border rounded-md"
              placeholder="Username"
            />
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="block w-full px-3 py-2 border rounded-md"
              placeholder="Password"
            />
          </div>

          {error && (
            <div className="bg-red-50 p-4 text-red-800 text-sm rounded">{error}</div>
          )}

          <Button type="submit" className="w-full" loading={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>
      </div>
    </div>
  );
}
EOF

echo "[3] Patch complete!"
echo "-----------------------------------------------------"
echo "Now restart the frontend:"
echo ""
echo "    cd ~/Desktop/truefypjs/frontend"
echo "    npm run dev -- --host"
echo ""
echo "Then login will work correctly."
