#!/usr/bin/env bash
# Builds the package and uploads it to the real PyPI.
# Usage: ./publish.sh
#
# Prerequisites (installed automatically if missing):
#   pip install build twine
#
# You will be prompted for your PyPI API token unless you have
# configured it in ~/.pypirc or via TWINE_* environment variables.
# To use a token, enter "__token__" as the username and paste the token as the password.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Installing / upgrading build tools ==="
python -m pip install --upgrade build twine

echo ""
echo "=== Cleaning previous builds ==="
rm -rf dist/

echo ""
echo "=== Building package ==="
python -m build

echo ""
echo "=== Uploading to PyPI ==="
python -m twine upload dist/*

echo ""
echo "=== Done! ==="
echo "Install with:"
echo "  pip install pajgps-api"

