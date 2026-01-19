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
      // Login with JumpServer API
      const r = await apiClient.post("/authentication/tokens/", {
        username,
        password,
      });

      // Save token
      localStorage.setItem("auth_token", r.data.token);

      // Redirect
      window.location.href = "/dashboard";
    } catch (err) {
      setError(err.response?.data?.error || "Invalid username or password.");
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
            <div>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Username"
                disabled={loading}
              />
            </div>

            <div>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Password"
                disabled={loading}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4 text-red-700 text-sm">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" loading={loading} disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      </div>
    </div>
  );
}
