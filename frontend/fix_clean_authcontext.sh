#!/bin/bash
set -e

FILE="src/contexts/AuthContext.jsx"

echo "[1] Removing all corrupted duplicate /users/... paths"
sed -i 's|/users/users/users/users/me/|/users/users/me/|g' "$FILE"
sed -i 's|/users/users/users/me/|/users/users/me/|g' "$FILE"
sed -i 's|/users/users/me/|/users/users/me/|g' "$FILE"
sed -i 's|/users/me/|/users/users/me/|g' "$FILE"

echo "[2] Restoring correct API calls"

# Fix the main ME endpoint
sed -i 's|apiClient.get(.*/users.*me.*|apiClient.get("/users/users/me/")|' "$FILE"

echo "[3] Fix MFA code block fetch"
sed -i 's|apiClient.get(.*/users.*users.*me.*|apiClient.get("/users/users/me/")|' "$FILE"

echo "[OK] AuthContext.jsx fully cleaned and fixed!"
