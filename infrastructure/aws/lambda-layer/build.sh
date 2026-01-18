#!/bin/bash
set -euo pipefail

# =============================================================================
# Lambda Layer Build Script
# Build Python dependencies for AWS Lambda Layer using uv
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
LAYER_DIR="${SCRIPT_DIR}/layer"
PYTHON_DIR="${LAYER_DIR}/python"

# Default values
PYTHON_VERSION="3.13"
PLATFORM="manylinux2014_x86_64"
ARCH="x86_64"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --python)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --arch)
            ARCH="$2"
            if [[ "$ARCH" == "arm64" ]]; then
                PLATFORM="manylinux2014_aarch64"
            else
                PLATFORM="manylinux2014_x86_64"
            fi
            shift 2
            ;;
        --clean)
            echo "Cleaning layer directory..."
            rm -rf "${LAYER_DIR}"
            exit 0
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --python VERSION  Python version (default: 3.13)"
            echo "  --arch ARCH       Architecture: x86_64 or arm64 (default: x86_64)"
            echo "  --clean           Clean layer directory and exit"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "============================================="
echo "Building Lambda Layer"
echo "============================================="
echo "Python version: ${PYTHON_VERSION}"
echo "Architecture: ${ARCH}"
echo "Platform: ${PLATFORM}"
echo "Project root: ${PROJECT_ROOT}"
echo "Layer directory: ${LAYER_DIR}"
echo "============================================="

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Clean and create layer directory
echo "Preparing layer directory..."
rm -rf "${LAYER_DIR}"
mkdir -p "${PYTHON_DIR}"

# Export dependencies using uv
echo "Exporting dependencies with uv..."
cd "${PROJECT_ROOT}"

# Generate requirements.txt from pyproject.toml
REQUIREMENTS_FILE="${LAYER_DIR}/requirements.txt"
echo "Generating requirements.txt..."
uv pip compile pyproject.toml -o "${REQUIREMENTS_FILE}" --python-version "${PYTHON_VERSION}"

# Install dependencies to the layer directory
echo "Installing dependencies to layer directory..."
uv pip install \
    --target "${PYTHON_DIR}" \
    -r "${REQUIREMENTS_FILE}"

# Remove temporary requirements file
rm -f "${REQUIREMENTS_FILE}"

# Remove unnecessary files to reduce layer size
# Note: Keep .dist-info for packages that use importlib.metadata
echo "Cleaning up unnecessary files..."
find "${PYTHON_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${PYTHON_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "${PYTHON_DIR}" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find "${PYTHON_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${PYTHON_DIR}" -type f -name "*.pyo" -delete 2>/dev/null || true

# Calculate layer size
LAYER_SIZE=$(du -sh "${LAYER_DIR}" | cut -f1)
echo "============================================="
echo "Build complete!"
echo "Layer size: ${LAYER_SIZE}"
echo "Layer path: ${LAYER_DIR}"
echo "============================================="
echo ""
echo "Next steps:"
echo "  1. Build SAM: sam build --config-env <env>"
echo "  2. Deploy:    sam deploy --config-env <env>"
echo ""
echo "Example (devel/staging/prod):"
echo "  sam build --config-env devel && sam deploy --config-env devel"
echo ""
echo "Stack name: prototype-app-lambda-layer-stack-{env}"
echo "Export:     prototype-app-layer-{env}"
