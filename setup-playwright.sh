#!/bin/bash
#
# Playwright Browser Installation Script
#
# This script installs Playwright browsers for Python Playwright library.
# Required for UI testing automation.
#
# Usage:
#   ./setup-playwright.sh              # Install chromium only (default)
#   ./setup-playwright.sh --all        # Install all browsers
#   ./setup-playwright.sh --with-deps  # Install chromium with system dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

log_info "Python version: $(python3 --version)"

# Check if playwright is installed
if ! python3 -c "import playwright" 2>/dev/null; then
    log_warn "Playwright Python package is not installed."
    log_info "Installing dependencies with uv..."
    
    # Check if uv is installed
    if command -v uv &> /dev/null; then
        log_info "Using uv for dependency installation"
        uv sync
    elif [ -f "requirements.txt" ]; then
        log_warn "uv not found, falling back to pip"
        pip install -r requirements.txt
    else
        log_warn "uv not found, installing playwright directly with pip"
        pip install playwright>=1.40.0
    fi
else
    log_info "Playwright Python package is installed"
fi

# Parse arguments
BROWSER_ARGS="chromium"
WITH_DEPS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            BROWSER_ARGS=""
            shift
            ;;
        --with-deps)
            WITH_DEPS="--with-deps"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --all         Install all browsers (chromium, firefox, webkit)"
            echo "  --with-deps   Install system dependencies (requires sudo)"
            echo "  -h, --help    Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Install chromium only"
            echo "  $0 --all              # Install all browsers"
            echo "  $0 --with-deps        # Install with system dependencies"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Install browsers
log_info "Installing Playwright browsers..."
log_info "Browser selection: ${BROWSER_ARGS:-all browsers}"

if [ -n "$WITH_DEPS" ]; then
    log_warn "Installing with system dependencies (may require sudo password)"
fi

# Run playwright install
if command -v uv &> /dev/null; then
    if uv run playwright install $WITH_DEPS $BROWSER_ARGS; then
        log_info "✓ Playwright browsers installed successfully"
    else
        log_error "Failed to install Playwright browsers"
        log_error "Try running with --with-deps if you're missing system dependencies"
        exit 1
    fi
else
    if python3 -m playwright install $WITH_DEPS $BROWSER_ARGS; then
        log_info "✓ Playwright browsers installed successfully"
    else
        log_error "Failed to install Playwright browsers"
        log_error "Try running with --with-deps if you're missing system dependencies"
        exit 1
    fi
fi

# Verify installation
log_info "Verifying browser installation..."

# Check for chromium (handle wildcards properly)
chromium_dirs=("$HOME"/.cache/ms-playwright/chromium* "$HOME"/Library/Caches/ms-playwright/chromium*)
chromium_found=false

for dir in "${chromium_dirs[@]}"; do
    if [ -d "$dir" ]; then
        chromium_found=true
        break
    fi
done

if [ "$chromium_found" = true ]; then
    log_info "✓ Chromium browser verified"
else
    log_warn "Chromium browser directory not found (may be in different location)"
fi

log_info ""
log_info "==================================="
log_info "Playwright Setup Complete!"
log_info "==================================="
log_info ""
log_info "You can now run UI tests:"
log_info "  ./cli.py --spec UI-001"
log_info "  ./cli.py --spec 'spider management'"
log_info ""
