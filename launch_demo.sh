#!/bin/bash

# StudyMate Demo Launcher
echo "🚀 Starting StudyMate Demo..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app_demo.py" ]; then
    echo "❌ Error: app_demo.py not found. Please run from the project root directory."
    exit 1
fi

# Add local bin to PATH for streamlit
export PATH="$HOME/.local/bin:$PATH"

# Launch the demo app
echo "📱 Launching StudyMate Demo on http://localhost:8501"
echo "🔗 The app will open in your default browser"
echo "⚠️  Note: This is a demo version showing UI and basic functionality"
echo ""
echo "To stop the app, press Ctrl+C"
echo "=================================="

# Run streamlit
streamlit run app_demo.py --server.port 8501 --server.address 0.0.0.0 --browser.gatherUsageStats false