#!/bin/bash

# AI Novel Writing Application Setup Script
# This script sets up the development environment for both backend and frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to check Node.js version
check_node() {
    if command_exists node; then
        NODE_VERSION=$(node -v | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        
        if [ "$NODE_MAJOR" -ge 16 ]; then
            print_success "Node.js $NODE_VERSION found"
            return 0
        else
            print_error "Node.js 16+ required, found $NODE_VERSION"
            return 1
        fi
    else
        print_error "Node.js not found"
        return 1
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Setup environment file
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Database Configuration
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
EOF
        print_warning "Please edit backend/.env with your OpenAI API key"
    fi
    
    # Initialize database
    print_status "Initializing database..."
    python -c "from db.database import init_db; init_db()"
    
    cd ..
    print_success "Backend setup complete!"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    cd ..
    print_success "Frontend setup complete!"
}

# Function to run tests
run_tests() {
    print_status "Running backend tests..."
    cd backend
    source venv/bin/activate
    python test_basic.py
    cd ..
    print_success "Tests completed!"
}

# Main setup function
main() {
    echo "=============================================="
    echo "  AI Novel Writing Application Setup"
    echo "=============================================="
    echo
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! check_python; then
        print_error "Please install Python 3.8+ and try again"
        exit 1
    fi
    
    if ! check_node; then
        print_error "Please install Node.js 16+ and try again"
        exit 1
    fi
    
    if ! command_exists npm; then
        print_error "npm not found. Please install Node.js with npm"
        exit 1
    fi
    
    print_success "All prerequisites met!"
    echo
    
    # Setup backend
    setup_backend
    echo
    
    # Setup frontend
    setup_frontend
    echo
    
    # Run tests
    run_tests
    echo
    
    # Final instructions
    echo "=============================================="
    echo "  Setup Complete!"
    echo "=============================================="
    echo
    print_success "Your AI Novel Writing Application is ready!"
    echo
    echo "Next steps:"
    echo "1. Edit backend/.env with your OpenAI API key"
    echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn app:app --reload"
    echo "3. Start the frontend: cd frontend && npm run dev"
    echo "4. Open http://localhost:3001 in your browser"
    echo
    echo "API Documentation: http://localhost:8000/docs"
    echo
    print_warning "Remember to keep your API keys secure and never commit them to version control!"
}

# Run main function
main "$@"
