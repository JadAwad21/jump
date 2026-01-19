#!/bin/bash
echo "[1] Fixing AuthContext (correct /users/me endpoint)..."
sed -i 's|/users/me/|/users/users/me/|g' src/contexts/AuthContext.jsx
sed -i 's|/users/me|/users/users/me|g' src/contexts/AuthContext.jsx

echo "[2] Fixing Login.jsx token handling..."
sed -i 's|await apiClient.post(.*/authentication/tokens/.*,|const r = await apiClient.post("/authentication/tokens/", { username, password });\n      localStorage.setItem("auth_token", r.data.token);|g' src/pages/Login.jsx

echo "[3] Ensuring redirect works..."
sed -i 's|navigate('/dashboard')|window.location.href = "/dashboard"|g' src/pages/Login.jsx

echo "[4] Patch complete!"
