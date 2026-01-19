#!/bin/bash
set -e

FILE="src/pages/Login.jsx"

echo "[1] Removing ALL corrupted token lines..."
sed -i '/const r = await apiClient.post/d' "$FILE"
sed -i '/localStorage.setItem("auth_token"/d' "$FILE"

echo "[2] Removing duplicate braces or leftovers..."
sed -i 's|username,||g' "$FILE"
sed -i 's|password,||g' "$FILE"

echo "[3] Inserting CLEAN working login logic..."

# Delete the entire block between "try {" and "catch"
sed -i '/try {/,/} catch (/d' "$FILE"

# Insert a fresh clean login block after "const handleSubmit"
sed -i '/const handleSubmit/a \
    try {\n\
      const r = await apiClient.post("/authentication/tokens/", { username, password });\n\
      localStorage.setItem("auth_token", r.data.token);\n\
      window.location.href = "/dashboard";\n\
    } catch (err) {\n\
      setError(err.response?.data?.error || "Login failed. Please check your credentials.");\n\
      setPassword("");\n\
    }' "$FILE"

echo "[DONE] Login.jsx fully repaired."
