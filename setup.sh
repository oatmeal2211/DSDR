#!/bin/bash

# Streamlit setup script for cloud deployment
echo "🚀 Setting up Streamlit dashboard for deployment..."

# Create necessary directories
mkdir -p .streamlit

# Download NLTK data if needed (for advanced text analysis)
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('✅ NLTK data downloaded')
except:
    print('⚠️ NLTK download skipped (optional)')
"

echo "✅ Setup complete!"