# PostgreSQL Setup Instructions

## Current Status
✅ **Backend Integration**: Complete - All services properly connected
✅ **Test Files**: Ready to run
❌ **PostgreSQL**: Not running (Docker Desktop needs to be started)

## Option 1: Start Docker Desktop (Recommended)

### Step 1: Start Docker Desktop
1. **Open Docker Desktop** from Start Menu or Desktop
2. **Wait for it to start** (may take 1-2 minutes)
3. **Verify it's running** by checking the Docker icon in system tray

### Step 2: Run PostgreSQL Container
Once Docker Desktop is running, execute these commands:

```bash
# Start PostgreSQL container
docker run -d --name qa-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=qa_system postgres:15

# Create the auth database
docker exec -it qa-postgres psql -U postgres -c "CREATE DATABASE qa_auth;"

# Run our setup script
python setup_postgresql.py
```

## Option 2: Install PostgreSQL Locally

### Step 1: Download PostgreSQL
1. Go to: https://www.postgresql.org/download/windows/
2. Download the Windows installer
3. Run the installer with default settings
4. **Remember the password** you set for the 'postgres' user

### Step 2: Run Setup Script
```bash
python setup_postgresql.py
```

## Option 3: Use Cloud Database (Alternative)

If you prefer a cloud solution:
1. **Supabase** (Free tier): https://supabase.com/
2. **Railway** (Free tier): https://railway.app/
3. **Neon** (Free tier): https://neon.tech/

Update the `.env` file with the cloud database URL.

## After PostgreSQL is Running

Once PostgreSQL is accessible, run:

```bash
# Setup database
python setup_postgresql.py

# Run comprehensive tests
python run_tests.py

# Start backend server
python start_backend.py
```

## Verification

The setup script will:
- ✅ Test PostgreSQL connection
- ✅ Create required databases
- ✅ Run all migrations
- ✅ Create default users
- ✅ Generate `.env` file
- ✅ Verify database integrity

## Default Credentials

After setup:
- **Client**: `client@demo.com` / `demo123`
- **Expert**: `expert@demo.com` / `demo123`
- **Admin**: `admin@demo.com` / `demo123`

## Troubleshooting

### Docker Issues
- Make sure Docker Desktop is running
- Check if port 5432 is available
- Try: `docker system prune` to clean up

### PostgreSQL Connection Issues
- Verify PostgreSQL is running: `docker ps` or check Windows services
- Check firewall settings
- Ensure port 5432 is not blocked

### Permission Issues
- Run terminal as Administrator if needed
- Check file permissions in project directory

## Next Steps

1. **Choose one of the options above**
2. **Get PostgreSQL running**
3. **Run the setup script**
4. **Test the integration**
5. **Start the backend server**

The backend is fully integrated and ready - we just need PostgreSQL running!


