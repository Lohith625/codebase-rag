#!/bin/bash
# Run code quality checks

echo "🔍 Running Code Quality Checks..."
echo "=================================="
echo ""

# 1. Format check with Black
echo "1️⃣ Checking code formatting (Black)..."
black --check backend scripts frontend 2>/dev/null
BLACK_EXIT=$?

if [ $BLACK_EXIT -eq 0 ]; then
    echo "   ✅ Code formatting: PASSED"
else
    echo "   ⚠️  Code formatting: FAILED (run: black backend scripts frontend)"
fi
echo ""

# 2. Lint with Flake8
echo "2️⃣ Linting code (Flake8)..."
flake8 backend --count --max-line-length=127 --statistics 2>/dev/null
FLAKE8_EXIT=$?

if [ $FLAKE8_EXIT -eq 0 ]; then
    echo "   ✅ Linting: PASSED"
else
    echo "   ⚠️  Linting: FAILED"
fi
echo ""

# 3. Type checking with mypy (optional)
echo "3️⃣ Type checking (mypy)..."
mypy backend --ignore-missing-imports 2>/dev/null
MYPY_EXIT=$?

if [ $MYPY_EXIT -eq 0 ]; then
    echo "   ✅ Type checking: PASSED"
else
    echo "   ⚠️  Type checking: FAILED (optional)"
fi
echo ""

# 4. Security check
echo "4️⃣ Security check (bandit)..."
pip show bandit > /dev/null 2>&1
if [ $? -eq 0 ]; then
    bandit -r backend -ll 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ Security: PASSED"
    else
        echo "   ⚠️  Security: Issues found"
    fi
else
    echo "   ℹ️  Bandit not installed (pip install bandit)"
fi
echo ""

# Summary
echo "=================================="
echo "📊 Quality Check Summary"
echo "=================================="
if [ $BLACK_EXIT -eq 0 ] && [ $FLAKE8_EXIT -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "⚠️  Some checks failed"
    exit 1
fi
