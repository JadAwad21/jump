#!/bin/bash

FILE="users/urls/api_urls.py"

# Check that the file exists
if [ ! -f "$FILE" ]; then
    echo "ERROR: $FILE not found! Run this inside apps/"
    exit 1
fi

# Check if alias already added
grep -q "user-me-alias" "$FILE"
if [ $? -eq 0 ]; then
    echo "[OK] Alias already exists. Nothing to do."
    exit 0
fi

echo "[INFO] Adding alias path('me/', UserProfileApi...) safely..."

# Insert alias BELOW existing 'users/me/' line
sed -i "/path('users\/me\/'/a \ \ \ \ path('me/', api.UserProfileApi.as_view(), name='user-me-alias')," "$FILE"

echo "[DONE] Alias added successfully!"
echo "[NEXT] Restart Django:  python3 manage.py runserver 0.0.0.0:8080"
