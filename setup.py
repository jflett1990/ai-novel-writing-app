#!/usr/bin/env python3
"""
AI Novel Writing Application Setup Script
Cross-platform setup script for the AI novel writing application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_status(message):
    """Print info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def run_command(command, cwd=None, check=True):
    """Run a shell command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print_error(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} found")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False


def check_node():
    """Check Node.js version."""
    try:
        result = run_command("node --version", check=False)
        if result.returncode == 0:
            version = result.stdout.strip().replace('v', '')
            major_version = int(version.split('.')[0])
            if major_version >= 16:
                print_success(f"Node.js {version} found")
                return True
            else:
                print_error(f"Node.js 16+ required, found {version}")
                return False
        else:
            print_error("Node.js not found")
            return False
    except Exception as e:
        print_error(f"Error checking Node.js: {e}")
        return False


def check_npm():
    """Check if npm is available."""
    try:
        result = run_command("npm --version", check=False)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"npm {version} found")
            return True
        else:
            print_error("npm not found")
            return False
    except Exception as e:
        print_error(f"Error checking npm: {e}")
        return False


def setup_backend():
    """Setup the backend environment."""
    print_status("Setting up backend...")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    
    # Create virtual environment
    if not venv_dir.exists():
        print_status("Creating Python virtual environment...")
        if platform.system() == "Windows":
            run_command("python -m venv venv", cwd=backend_dir)
        else:
            run_command("python3 -m venv venv", cwd=backend_dir)
    
    # Determine activation script and commands
    if platform.system() == "Windows":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_cmd = f"venv\\Scripts\\pip"
        python_cmd = f"venv\\Scripts\\python"
    else:
        activate_script = venv_dir / "bin" / "activate"
        pip_cmd = f"venv/bin/pip"
        python_cmd = f"venv/bin/python"
    
    # Upgrade pip
    print_status("Upgrading pip...")
    run_command(f"{pip_cmd} install --upgrade pip", cwd=backend_dir)
    
    # Install dependencies
    print_status("Installing Python dependencies...")
    run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
    
    # Setup environment file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print_status("Creating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=sqlite:///./ai_novel_app.db

# AI Provider Settings
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Ollama Settings (for local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3001"]

# Generation Settings
MAX_CHAPTERS_PER_STORY=50
DEFAULT_CHAPTER_LENGTH=2000
GENERATION_TIMEOUT=300

# Writing Complexity
NOVEL_COMPLEXITY=standard
"""
        env_file.write_text(env_content)
        print_warning("Please edit backend/.env with your OpenAI API key")
    
    # Initialize database
    print_status("Initializing database...")
    run_command(f'{python_cmd} -c "from db.database import init_db; init_db()"', cwd=backend_dir)
    
    print_success("Backend setup complete!")


def setup_frontend():
    """Setup the frontend environment."""
    print_status("Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print_status("Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    print_success("Frontend setup complete!")


def run_tests():
    """Run backend tests."""
    print_status("Running backend tests...")

    backend_dir = Path("backend")

    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"

    run_command(f"{python_cmd} test_basic.py", cwd=backend_dir)
    print_success("Tests completed!")


def main():
    """Main setup function."""
    print("=" * 50)
    print("  AI Novel Writing Application Setup")
    print("=" * 50)
    print()
    
    # Check prerequisites
    print_status("Checking prerequisites...")
    
    if not check_python():
        print_error("Please install Python 3.8+ and try again")
        sys.exit(1)
    
    if not check_node():
        print_error("Please install Node.js 16+ and try again")
        sys.exit(1)
    
    if not check_npm():
        print_error("Please install npm and try again")
        sys.exit(1)
    
    print_success("All prerequisites met!")
    print()
    
    # Setup backend
    setup_backend()
    print()
    
    # Setup frontend
    setup_frontend()
    print()
    
    # Run tests
    run_tests()
    print()
    
    # Final instructions
    print("=" * 50)
    print("  Setup Complete!")
    print("=" * 50)
    print()
    print_success("Your AI Novel Writing Application is ready!")
    print()
    print("Next steps:")
    print("1. Edit backend/.env with your OpenAI API key")
    
    if platform.system() == "Windows":
        print("2. Start the backend: cd backend && venv\\Scripts\\activate && uvicorn app:app --reload")
    else:
        print("2. Start the backend: cd backend && source venv/bin/activate && uvicorn app:app --reload")
    
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:3001 in your browser")
    print()
    print("API Documentation: http://localhost:8000/docs")
    print()
    print_warning("Remember to keep your API keys secure and never commit them to version control!")


if __name__ == "__main__":
    main()
