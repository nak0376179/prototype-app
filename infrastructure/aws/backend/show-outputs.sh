#!/bin/bash
set -euo pipefail

# =============================================================================
# Show Backend Stack Outputs
# =============================================================================

PROJECT_NAME="prototype-app"
ENV="${1:-devel}"
STACK_NAME="${PROJECT_NAME}-backend-stack-${ENV}"

# Validate environment
if [[ ! "$ENV" =~ ^(devel|staging|prod)$ ]]; then
    echo "Error: Invalid environment '${ENV}'"
    echo "Usage: $0 [devel|staging|prod]"
    exit 1
fi

echo "============================================="
echo "Stack: ${STACK_NAME}"
echo "============================================="

# Check if stack exists
if ! aws cloudformation describe-stacks --stack-name "${STACK_NAME}" &>/dev/null; then
    echo "Error: Stack '${STACK_NAME}' does not exist"
    exit 1
fi

# Get outputs
aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query 'Stacks[0].Outputs[*].[OutputKey, OutputValue]' \
    --output table

echo ""
echo "Exports:"
echo "  API URL: ${PROJECT_NAME}-api-url-${ENV}"
echo "  API ID:  ${PROJECT_NAME}-api-id-${ENV}"
