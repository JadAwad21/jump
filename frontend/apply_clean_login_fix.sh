#!/bin/bash
echo "[PATCH] Applying clean Login.jsx token patch..."

sed -i "/try {/a \
      const r = await apiClient.post(\"/authentication/tokens/\", { username, password });\
      localStorage.setItem(\"auth_token\", r.data.token);" src/pages/Login.jsx

sed -i "s|navigate('/dashboard')|window.location.href = '/dashboard'|g" src/pages/Login.jsx

echo "[DONE] Login.jsx patched correctly."
