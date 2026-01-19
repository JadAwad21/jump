#!/bin/bash
echo "[RESTORE] Cleaning broken patch in Login.jsx..."

# Remove any duplicated 'const response = const r'
sed -i 's|const response = const r|const r|' src/pages/Login.jsx

# Remove leftover junk braces accidentally inserted
sed -i 's|localStorage.setItem("auth_token", r.data.token); {|localStorage.setItem("auth_token", r.data.token);|g' src/pages/Login.jsx
sed -i 's|username,||g' src/pages/Login.jsx
sed -i 's|password,||g' src/pages/Login.jsx

echo "[DONE] Login.jsx cleaned."
