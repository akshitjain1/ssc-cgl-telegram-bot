#!/bin/bash
# Deploy preparation script for SSC-CGL Bot

echo "🚀 Preparing SSC-CGL Bot for Render.com deployment..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Run this script from the project root directory."
    exit 1
fi

echo "📦 Updating requirements.txt..."
pip freeze > requirements.txt

echo "✅ Checking required files..."
required_files=("Procfile" "start.sh" "main.py" "requirements.txt")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    else
        echo "  ✓ $file"
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    printf '  - %s\n' "${missing_files[@]}"
    exit 1
fi

echo "🔧 Making start.sh executable..."
chmod +x start.sh

echo "📋 Deployment checklist:"
echo "  ✓ Procfile created"
echo "  ✓ start.sh script ready"
echo "  ✓ requirements.txt updated"
echo "  ✓ All core files present"

echo ""
echo "🌐 Next steps for Render.com deployment:"
echo "1. Commit and push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Prepare for Render deployment'"
echo "   git push origin main"
echo ""
echo "2. Go to render.com and create a new Web Service"
echo "3. Connect your GitHub repository"
echo "4. Add environment variables from .env.production template"
echo "5. Deploy!"
echo ""
echo "📖 See RENDER_DEPLOYMENT.md for detailed instructions"
echo "🎉 Your bot will be running 24x7 once deployed!"
