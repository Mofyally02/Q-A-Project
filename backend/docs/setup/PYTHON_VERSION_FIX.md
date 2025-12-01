# Python Version Compatibility Fix

## Problem

Python 3.14 is very new and many packages don't support it yet:
- `asyncpg` - Cython compilation errors
- `psycopg2-binary` - Deprecated API usage
- `pydantic-core` - ForwardRef API changes

## Solution

**Use Python 3.12 or 3.13 instead** (recommended for production)

### Option 1: Install Python 3.13 (Recommended)

```bash
# Install Python 3.13
brew install python@3.13

# Create new virtual environment with Python 3.13
cd backend
rm -rf venv
python3.13 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Start server
./start_server.sh
```

### Option 2: Install Python 3.12

```bash
# Install Python 3.12
brew install python@3.12

# Create new virtual environment with Python 3.12
cd backend
rm -rf venv
python3.12 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Start server
./start_server.sh
```

### Option 3: Use pyenv (Best for managing multiple Python versions)

```bash
# Install pyenv
brew install pyenv

# Install Python 3.13
pyenv install 3.13.0

# Set local Python version
cd backend
pyenv local 3.13.0

# Create virtual environment
rm -rf venv
python -m venv venv

# Continue with installation
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Updated Requirements

The `requirements.txt` has been updated to use more flexible version constraints:
- `asyncpg>=0.29.0` (was `==0.29.0`)
- `psycopg2-binary>=2.9.9` (was `==2.9.9`)
- `pydantic>=2.9.0` (was `==2.5.0`)
- `pydantic-settings>=2.5.0` (was `==2.1.0`)
- `email-validator>=2.2.0` (was `==2.1.0`)

## Quick Fix Command

```bash
cd backend
rm -rf venv
brew install python@3.13
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
./start_server.sh
```

## Verify Python Version

```bash
python --version
# Should show: Python 3.13.x or Python 3.12.x
```

---

**Note:** The `start_server.sh` script now detects Python 3.14 and warns you, but will try to use Python 3.13 or 3.12 if available.

