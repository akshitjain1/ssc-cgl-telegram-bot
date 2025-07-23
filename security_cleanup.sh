#!/bin/bash
# Security Cleanup Script - Remove sensitive files and secure the repository

echo "🔒 Starting Security Cleanup..."

# 1. Remove sensitive files outside the repository
echo "📁 Cleaning up sensitive files outside repository..."
if [ -f "../api keys.txt" ]; then
    echo "⚠️  Found sensitive file: ../api keys.txt"
    echo "🗑️  Removing ../api keys.txt..."
    rm -f "../api keys.txt"
    echo "✅ Removed ../api keys.txt"
else
    echo "✅ No ../api keys.txt found"
fi

# 2. Check for any .env files with real secrets
echo "🔍 Checking for .env files with real secrets..."
if [ -f ".env" ]; then
    if grep -q "8034557764\|AIzaSyC4eg3m_15VR3467tWN7DgId_GafvXc9us\|5c73199076cf47e6b80b75c08a1f6910" .env; then
        echo "⚠️  Found real API keys in .env file"
        echo "🔄 Creating backup of .env..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo "🧹 Please manually update .env with placeholder values"
    else
        echo "✅ .env file appears to have placeholder values"
    fi
fi

# 3. Secure database directory permissions
echo "🔐 Setting secure permissions for database directory..."
if [ -d "database" ]; then
    chmod 700 database/
    echo "✅ Database directory permissions set to 700"
fi

# 4. Check for any other sensitive files
echo "🔍 Scanning for other sensitive files..."
find . -name "*.key" -o -name "*.pem" -o -name "*secret*" -o -name "*password*" -o -name "config.ini" 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        echo "⚠️  Found potentially sensitive file: $file"
    fi
done

# 5. Verify .gitignore is protecting sensitive files
echo "🛡️  Verifying .gitignore protection..."
if git check-ignore .env >/dev/null 2>&1; then
    echo "✅ .env is properly ignored by git"
else
    echo "❌ .env is NOT ignored by git - this is dangerous!"
fi

# 6. Check git status for any staged sensitive files
echo "📋 Checking git status for sensitive files..."
if git status --porcelain | grep -E "\.(env|key|pem|p12)|\bsecret\b|\bpassword\b|\bapi.*key\b"; then
    echo "⚠️  WARNING: Potentially sensitive files are staged for commit!"
    echo "🛑 Please review and unstage these files before committing"
else
    echo "✅ No sensitive files detected in git staging area"
fi

# 7. Environment validation
echo "🔧 Validating environment variables..."
if [ -z "$BOT_TOKEN" ] || [[ "$BOT_TOKEN" == "your_"* ]]; then
    echo "✅ BOT_TOKEN is not set or is placeholder (good for repo)"
else
    echo "⚠️  BOT_TOKEN appears to be set to real value"
fi

echo ""
echo "🎯 Security Cleanup Complete!"
echo ""
echo "📝 Manual Steps Required:"
echo "1. Ensure your production environment has real API keys"
echo "2. Keep .env file with placeholder values only"
echo "3. Use environment variables in production (Render.com)"
echo "4. Regularly rotate your API keys"
echo "5. Monitor for any accidental commits of secrets"
echo ""
echo "🔒 Security Best Practices:"
echo "• Never commit real API keys to git"
echo "• Use different keys for development and production"
echo "• Enable 2FA on all service accounts"
echo "• Regularly audit your repository for secrets"
echo "• Use GitHub secret scanning if available"
