===============================================================================
TRUEFYPJS BLOCKCHAIN DASHBOARDS - INSTALLATION GUIDE
===============================================================================

YOU RECEIVED 3 FILES:
1. back.txt               - Backend code (6 files)
2. front.txt              - Frontend code (7 files)  
3. INSTALL_BLOCKCHAIN.sh  - Auto installer

===============================================================================
INSTALLATION (3 COMMANDS)
===============================================================================

cd ~/Desktop/truefypjs
chmod +x INSTALL_BLOCKCHAIN.sh
./INSTALL_BLOCKCHAIN.sh

That's it! Script does everything automatically.

===============================================================================
AFTER INSTALLATION - START SERVERS
===============================================================================

Terminal 1 - Backend:
cd ~/Desktop/truefypjs/apps
source ../venv/bin/activate
python manage.py runserver 0.0.0.0:8080

Terminal 2 - Frontend:
cd ~/Desktop/truefypjs/frontend
npm run dev

===============================================================================
TEST THE INSTALLATION
===============================================================================

1. Browser: http://localhost:3000
2. Login: admin / Admin@12345
3. Create user with "Investigator" role
4. Go to "Certificates" tab
5. Issue certificate for that user
6. Logout
7. Login as new user
8. ✅ You'll see Investigator Dashboard!

===============================================================================
WHAT THIS ADDS
===============================================================================

✅ Investigator Dashboard - Create investigations, upload evidence (with GUID)
✅ Auditor Dashboard - Read-only (anonymous names hidden)
✅ Court Dashboard - Read-only + GUID resolver (reveal real names)

===============================================================================
TROUBLESHOOTING
===============================================================================

Error: "permission denied"
Fix: chmod +x INSTALL_BLOCKCHAIN.sh

Error: PostgreSQL connection failed
Fix: Make sure PostgreSQL is running

Error: Module not found
Fix: cd apps && python manage.py migrate blockchain --fake

Error: No dashboard appears
Fix: User needs both role AND certificate

===============================================================================
