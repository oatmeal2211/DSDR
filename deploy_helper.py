"""
🚀 Airline Dashboard Deployment Helper
=====================================

This script helps you deploy your dashboard to the web quickly and easily.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_git_installed():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_git_repo():
    """Check if current directory is a git repository"""
    return os.path.exists('.git')

def initialize_git_repo():
    """Initialize a new git repository"""
    print("🔧 Initializing Git repository...")
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        print("✅ Git repository initialized!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error initializing Git: {e}")
        return False

def create_gitignore():
    """Create .gitignore file for Python projects"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Jupyter Notebook
.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Local environment variables
.env
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")

def commit_files():
    """Add and commit all files"""
    print("📦 Adding files to Git...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial airline dashboard commit"], check=True)
        print("✅ Files committed to Git!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error committing files: {e}")
        return False

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n🚀 DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    
    print("\n📋 **Step 1: Create GitHub Repository**")
    print("1. Go to https://github.com")
    print("2. Click 'New repository'")
    print("3. Name it: 'airline-dashboard'")
    print("4. Make it public (required for free Streamlit hosting)")
    print("5. Don't initialize with README (we have files already)")
    print("6. Click 'Create repository'")
    
    print("\n📤 **Step 2: Push Your Code**")
    print("Copy and run these commands in your terminal:")
    print(f"   git remote add origin https://github.com/YOUR_USERNAME/airline-dashboard.git")
    print(f"   git push -u origin main")
    
    print("\n🌐 **Step 3: Deploy to Streamlit Community Cloud**")
    print("1. Go to https://share.streamlit.io")
    print("2. Sign in with your GitHub account")
    print("3. Click 'New app'")
    print("4. Select repository: 'airline-dashboard'")
    print("5. Main file path: 'advanced_airline_dashboard.py'")
    print("6. Click 'Deploy!'")
    
    print("\n✨ **Your dashboard will be live at:**")
    print("   https://YOUR_USERNAME-airline-dashboard-advanced-airline-dashboard-xyz.streamlit.app")
    
    print("\n🎯 **Alternative Deployment Options:**")
    print("• Heroku: https://heroku.com (free tier)")
    print("• Railway: https://railway.app (modern platform)")
    print("• Render: https://render.com (simple deployment)")

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        'advanced_airline_dashboard.py',
        'Airline Review.csv',
        'requirements_advanced.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found!")
    return True

def main():
    """Main deployment helper function"""
    print("🚀 Airline Dashboard Deployment Helper")
    print("=" * 45)
    
    # Check required files
    if not check_required_files():
        print("\n💡 Please ensure all required files are present before deployment.")
        return
    
    # Check Git installation
    if not check_git_installed():
        print("❌ Git is not installed!")
        print("💡 Please install Git from: https://git-scm.com/downloads")
        return
    
    print("✅ Git is installed!")
    
    # Check if Git repo exists
    if not check_git_repo():
        print("📂 No Git repository found.")
        init_repo = input("Initialize Git repository? (y/n): ").lower().strip()
        if init_repo in ['y', 'yes']:
            if not initialize_git_repo():
                return
        else:
            print("⚠️ Git repository required for deployment.")
            return
    else:
        print("✅ Git repository found!")
    
    # Create .gitignore if needed
    create_gitignore()
    
    # Commit files
    commit_choice = input("\n📦 Commit current files to Git? (y/n): ").lower().strip()
    if commit_choice in ['y', 'yes']:
        if not commit_files():
            print("⚠️ Continuing with deployment instructions...")
    
    # Show deployment instructions
    show_deployment_instructions()
    
    print("\n🎉 **Ready for Deployment!**")
    print("Your dashboard includes:")
    print("• Interactive analytics with filters")
    print("• Comprehensive satisfaction analysis")
    print("• Competitive landscape insights")
    print("• Geographic performance analysis")
    print("• Professional styling and layouts")
    
    print("\n💡 **Pro Tips:**")
    print("• Keep your GitHub repo public for free Streamlit hosting")
    print("• Your dashboard will auto-update when you push changes")
    print("• Add Google Analytics for usage tracking")
    print("• Consider custom domain for professional presentation")

if __name__ == "__main__":
    main()