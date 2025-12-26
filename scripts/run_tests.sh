#!/bin/bash
# Run all tests with coverage

echo "🧪 Running Codebase RAG Tests..."
echo "=================================="
echo ""

# Run tests with coverage
pytest tests/ \
    -v \
    --cov=backend \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report: htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
