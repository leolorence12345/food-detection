#!/bin/bash
# Check pipeline status

cd "$(dirname "$0")"

echo "=========================================="
echo "Pipeline Status Check"
echo "=========================================="
echo ""

# Check running processes
echo "1. Running Python processes:"
ps aux | grep python | grep -v grep | head -5 || echo "   No Python processes running"
echo ""

# Check Docker containers
echo "2. Docker containers:"
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}" | head -5 || echo "   No Docker containers running"
echo ""

# Check recent output directories
echo "3. Recent output directories:"
ls -lth data/outputs/ 2>/dev/null | head -5 || echo "   No output directories"
echo ""

# Check for results.json
echo "4. Results file:"
if [ -f "results.json" ]; then
    echo "   ✓ results.json exists"
    echo "   Size: $(ls -lh results.json | awk '{print $5}')"
    echo "   Modified: $(ls -lth results.json | awk '{print $6, $7, $8}')"
else
    echo "   ✗ results.json not found"
fi
echo ""

# Check latest output directory
LATEST_RUN=$(ls -t data/outputs/ 2>/dev/null | head -1)
if [ -n "$LATEST_RUN" ]; then
    echo "5. Latest run: $LATEST_RUN"
    echo "   Files:"
    find "data/outputs/$LATEST_RUN" -type f | head -5
    echo ""
fi

# Check for errors
echo "6. Recent errors (if any):"
find . -name "*.log" -mmin -60 -exec tail -5 {} \; 2>/dev/null | grep -i error | head -5 || echo "   No recent errors found"
echo ""

echo "=========================================="
echo "If pipeline is running, check terminal output"
echo "Models may take 2-5 minutes to download"
echo "=========================================="


