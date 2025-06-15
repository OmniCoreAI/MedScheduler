#!/bin/bash

# MediBook - Dual Server Startup Script
# Runs both FastAPI and Streamlit frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
FASTAPI_PORT=${PORT:-8001}
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}
FASTAPI_PID_FILE="$SCRIPT_DIR/.fastapi.pid"
STREAMLIT_PID_FILE="$SCRIPT_DIR/.streamlit.pid"

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${PURPLE}🏥 MediBook - AI Medical Appointment Booking${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

check_requirements() {
    print_status "Checking requirements..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    # Install/update requirements
    print_status "Installing/updating requirements..."
    pip install -q -r requirements.txt
    print_success "Requirements installed"
}

setup_environment() {
    print_status "Setting up environment..."
    
    # Load environment variables if .env exists
    if [ -f "$ENV_FILE" ]; then
        print_status "Loading environment variables from .env"
        # Use set -a to automatically export variables, then source the file
        set -a
        source "$ENV_FILE"
        set +a
    else
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your OpenAI API key"
        print_status "You can get your API key from: https://platform.openai.com/api-keys"
        read -p "Press Enter after you've updated the .env file..."
        set -a
        source .env
        set +a
    fi
    
    # Update ports from environment
    FASTAPI_PORT=${PORT:-8000}
    STREAMLIT_PORT=${STREAMLIT_PORT:-8501}
    
    print_success "Environment configured"
    print_status "FastAPI will run on port: $FASTAPI_PORT"
    print_status "Streamlit will run on port: $STREAMLIT_PORT"
}

check_ports() {
    print_status "Checking if ports are available..."
    
    # Check FastAPI port
    if lsof -Pi :$FASTAPI_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $FASTAPI_PORT is already in use"
        print_status "Attempting to kill existing process..."
        lsof -ti:$FASTAPI_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Check Streamlit port
    if lsof -Pi :$STREAMLIT_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $STREAMLIT_PORT is already in use"
        print_status "Attempting to kill existing process..."
        lsof -ti:$STREAMLIT_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    print_success "Ports are available"
}

start_fastapi() {
    print_status "Starting FastAPI backend server..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Start FastAPI in background
    nohup python main.py > fastapi.log 2>&1 &
    FASTAPI_PID=$!
    echo $FASTAPI_PID > "$FASTAPI_PID_FILE"
    
    # Wait for FastAPI to start
    print_status "Waiting for FastAPI to start..."
    for i in {1..30}; do
        if curl -s "http://localhost:$FASTAPI_PORT/health" >/dev/null 2>&1; then
            print_success "FastAPI backend started successfully (PID: $FASTAPI_PID)"
            print_status "Backend available at: http://localhost:$FASTAPI_PORT"
            print_status "API docs available at: http://localhost:$FASTAPI_PORT/docs"
            return 0
        fi
        sleep 1
    done
    
    print_error "FastAPI failed to start within 30 seconds"
    return 1
}

start_streamlit() {
    print_status "Starting Streamlit frontend..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Start Streamlit in background
    nohup streamlit run streamlit_app.py \
        --server.port $STREAMLIT_PORT \
        --server.address 0.0.0.0 \
        --browser.gatherUsageStats false \
        --server.headless true \
        > streamlit.log 2>&1 &
    
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > "$STREAMLIT_PID_FILE"
    
    # Wait for Streamlit to start
    print_status "Waiting for Streamlit to start..."
    for i in {1..30}; do
        if curl -s "http://localhost:$STREAMLIT_PORT" >/dev/null 2>&1; then
            print_success "Streamlit frontend started successfully (PID: $STREAMLIT_PID)"
            print_status "Frontend available at: http://localhost:$STREAMLIT_PORT"
            return 0
        fi
        sleep 1
    done
    
    print_error "Streamlit failed to start within 30 seconds"
    return 1
}

stop_servers() {
    print_status "Stopping servers..."
    
    # Stop FastAPI
    if [ -f "$FASTAPI_PID_FILE" ]; then
        FASTAPI_PID=$(cat "$FASTAPI_PID_FILE")
        if kill -0 $FASTAPI_PID 2>/dev/null; then
            kill $FASTAPI_PID
            print_success "FastAPI server stopped"
        fi
        rm -f "$FASTAPI_PID_FILE"
    fi
    
    # Stop Streamlit
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        STREAMLIT_PID=$(cat "$STREAMLIT_PID_FILE")
        if kill -0 $STREAMLIT_PID 2>/dev/null; then
            kill $STREAMLIT_PID
            print_success "Streamlit server stopped"
        fi
        rm -f "$STREAMLIT_PID_FILE"
    fi
    
    # Kill any remaining processes on the ports
    lsof -ti:$FASTAPI_PORT | xargs kill -9 2>/dev/null || true
    lsof -ti:$STREAMLIT_PORT | xargs kill -9 2>/dev/null || true
}

show_status() {
    print_header
    print_status "Server Status:"
    echo ""
    
    # Check FastAPI
    if curl -s "http://localhost:$FASTAPI_PORT/health" >/dev/null 2>&1; then
        print_success "✅ FastAPI Backend: Running on http://localhost:$FASTAPI_PORT"
        print_status "   📚 API Docs: http://localhost:$FASTAPI_PORT/docs"
    else
        print_error "❌ FastAPI Backend: Not running"
    fi
    
    # Check Streamlit
    if curl -s "http://localhost:$STREAMLIT_PORT" >/dev/null 2>&1; then
        print_success "✅ Streamlit Frontend: Running on http://localhost:$STREAMLIT_PORT"
    else
        print_error "❌ Streamlit Frontend: Not running"
    fi
    
    echo ""
}

cleanup() {
    print_status "Cleaning up..."
    stop_servers
    print_success "Cleanup completed"
    exit 0
}

# Signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
case "${1:-start}" in
    "start")
        print_header
        check_requirements
        setup_environment
        check_ports
        
        print_status "Starting MediBook servers..."
        echo ""
        
        if start_fastapi && start_streamlit; then
            echo ""
            print_success "🎉 MediBook is now running!"
            echo ""
            print_status "📍 Access points:"
            print_status "   🎨 Web Interface: http://localhost:$STREAMLIT_PORT"
            print_status "   🔧 API Backend: http://localhost:$FASTAPI_PORT"
            print_status "   📚 API Documentation: http://localhost:$FASTAPI_PORT/docs"
            echo ""
            print_status "Press Ctrl+C to stop both servers"
            echo ""
            
            # Keep script running and monitor servers
            while true; do
                sleep 10
                # Check if servers are still running
                if [ -f "$FASTAPI_PID_FILE" ] && [ -f "$STREAMLIT_PID_FILE" ]; then
                    FASTAPI_PID=$(cat "$FASTAPI_PID_FILE")
                    STREAMLIT_PID=$(cat "$STREAMLIT_PID_FILE")
                    
                    if ! kill -0 $FASTAPI_PID 2>/dev/null || ! kill -0 $STREAMLIT_PID 2>/dev/null; then
                        print_error "One or more servers have stopped unexpectedly"
                        cleanup
                    fi
                else
                    print_error "PID files missing"
                    cleanup
                fi
            done
        else
            print_error "Failed to start servers"
            cleanup
            exit 1
        fi
        ;;
    
    "stop")
        print_header
        stop_servers
        print_success "All servers stopped"
        ;;
    
    "restart")
        print_header
        stop_servers
        sleep 2
        exec "$0" start
        ;;
    
    "status")
        show_status
        ;;
    
    "logs")
        print_header
        print_status "Server logs:"
        echo ""
        echo -e "${YELLOW}=== FastAPI Logs ===${NC}"
        tail -n 20 fastapi.log 2>/dev/null || echo "No FastAPI logs found"
        echo ""
        echo -e "${YELLOW}=== Streamlit Logs ===${NC}"
        tail -n 20 streamlit.log 2>/dev/null || echo "No Streamlit logs found"
        ;;
    
    "help"|"-h"|"--help")
        print_header
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start both servers (default)"
        echo "  stop     - Stop both servers"
        echo "  restart  - Restart both servers"
        echo "  status   - Show server status"
        echo "  logs     - Show recent server logs"
        echo "  help     - Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  PORT              - FastAPI port (default: 8001)"
        echo "  STREAMLIT_PORT    - Streamlit port (default: 8501)"
        echo "  OPENAI_API_KEY    - Your OpenAI API key (required)"
        echo ""
        ;;
    
    *)
        print_error "Unknown command: $1"
        print_status "Use '$0 help' for usage information"
        exit 1
        ;;
esac 