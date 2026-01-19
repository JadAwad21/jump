#!/bin/bash
set -e

echo "=========================================="
echo "TruefyPJS Blockchain Dashboards Installer"
echo "=========================================="
echo ""

# Check directory
if [ ! -f "apps/manage.py" ]; then
    echo "❌ ERROR: Run from TruefyPJS root directory"
    exit 1
fi

echo "✓ Correct directory"
echo ""

# Step 1: Backend files
echo "[1/5] Creating backend files..."
source venv/bin/activate
mkdir -p BLOCKCHAIN_PACKAGE/apps/blockchain/api
cd BLOCKCHAIN_PACKAGE
bash ../back.txt
cd ..
echo "✓ Backend files created"
echo ""

# Step 2: Frontend files  
echo "[2/5] Creating frontend files..."
cd BLOCKCHAIN_PACKAGE
bash ../front.txt
cd ..
echo "✓ Frontend files created"
echo ""

# Step 3: Copy files to actual locations
echo "[3/5] Copying files to project..."
cp -r BLOCKCHAIN_PACKAGE/apps/* apps/
cp -r BLOCKCHAIN_PACKAGE/frontend/* frontend/
echo "✓ Files copied"
echo ""

# Step 4: Database setup
echo "[4/5] Setting up database..."
cd apps
PGPASSWORD=jsroot psql -h localhost -U jsroot -d jumpserver << 'SQL'
DROP TABLE IF EXISTS blockchain_transaction CASCADE;
DROP TABLE IF EXISTS blockchain_evidence CASCADE;
DROP TABLE IF EXISTS blockchain_investigation CASCADE;
DROP TABLE IF EXISTS blockchain_investigation_tag CASCADE;
DROP TABLE IF EXISTS blockchain_investigation_note CASCADE;
DROP TABLE IF EXISTS blockchain_investigation_activity CASCADE;
DROP TABLE IF EXISTS blockchain_tag CASCADE;
DROP TABLE IF EXISTS blockchain_guid_mapping CASCADE;

CREATE TABLE blockchain_investigation (id UUID PRIMARY KEY, title VARCHAR(255) NOT NULL, description TEXT NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'open', created_by_id UUID NOT NULL REFERENCES users_user(id), created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), blockchain_tx_hash VARCHAR(66), blockchain_block INTEGER);
CREATE TABLE blockchain_tag (id UUID PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL, color VARCHAR(7) DEFAULT '#3B82F6', created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW());
CREATE TABLE blockchain_evidence (id UUID PRIMARY KEY, investigation_id UUID NOT NULL REFERENCES blockchain_investigation(id), title VARCHAR(255) NOT NULL, description TEXT, file_name VARCHAR(255) NOT NULL, file_hash VARCHAR(64) NOT NULL, file_size BIGINT NOT NULL, ipfs_hash VARCHAR(100), ipfs_uploaded BOOLEAN DEFAULT FALSE, blockchain_tx_hash VARCHAR(66), blockchain_block INTEGER, uploaded_by_id UUID REFERENCES users_user(id), uploaded_anonymously BOOLEAN DEFAULT FALSE, anonymous_guid UUID, uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW());
CREATE TABLE blockchain_investigation_tag (id SERIAL PRIMARY KEY, investigation_id UUID NOT NULL REFERENCES blockchain_investigation(id), tag_id UUID NOT NULL REFERENCES blockchain_tag(id), UNIQUE(investigation_id, tag_id));
CREATE TABLE blockchain_guid_mapping (id UUID PRIMARY KEY, guid UUID UNIQUE NOT NULL, investigator_id UUID REFERENCES users_user(id), created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW());
CREATE TABLE blockchain_transaction (id UUID PRIMARY KEY, tx_hash VARCHAR(66) UNIQUE NOT NULL, block_number INTEGER NOT NULL, tx_type VARCHAR(50) NOT NULL, data JSONB NOT NULL, user_id UUID REFERENCES users_user(id), user_guid UUID, timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW());
CREATE TABLE blockchain_investigation_note (id UUID PRIMARY KEY, investigation_id UUID NOT NULL REFERENCES blockchain_investigation(id), content TEXT NOT NULL, created_by_id UUID NOT NULL REFERENCES users_user(id), created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW());
CREATE TABLE blockchain_investigation_activity (id UUID PRIMARY KEY, investigation_id UUID NOT NULL REFERENCES blockchain_investigation(id), activity_type VARCHAR(50) NOT NULL, description TEXT NOT NULL, created_by_id UUID REFERENCES users_user(id), created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW());
SQL

cd blockchain/migrations && rm -f 0*.py && cd ../..
python manage.py makemigrations blockchain 2>&1 | grep -v "UserWarning" || true
python manage.py migrate blockchain 2>&1 | grep -v "UserWarning" || true
cd ..
echo "✓ Database setup complete"
echo ""

# Step 5: Create roles
echo "[5/5] Creating blockchain roles..."
cd apps
python manage.py shell << 'PYEOF' 2>&1 | grep -v "UserWarning"
from rbac.models import Role
for name in ['Investigator', 'Auditor', 'Court']:
    Role.objects.get_or_create(name=name, defaults={'scope': 'system'})
    print(f"✓ Created role: {name}")
PYEOF
cd ..
echo ""

echo "=========================================="
echo "✅ INSTALLATION COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start backend:  cd apps && python manage.py runserver 0.0.0.0:8080"
echo "2. Start frontend: cd frontend && npm run dev"  
echo "3. Login as admin, create users with Investigator/Auditor/Court roles"
echo "4. Issue certificates for those users (Admin → Certificates)"
echo "5. Test by logging in as those users"
echo ""
